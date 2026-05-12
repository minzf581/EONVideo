import { unlink } from "node:fs/promises";

import { claimPendingJob, closeDb, ensureRenderJobsTable, markJobCompleted, markJobFailed } from "./db.js";
import { renderJobVideo } from "./render.js";
import { uploadMp4 } from "./r2.js";

const pollIntervalMs = 5000;
const concurrency = Math.max(1, Number(process.env.WORKER_CONCURRENCY ?? "1"));
let shuttingDown = false;
let active = 0;

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function processNextJob(): Promise<boolean> {
  const job = await claimPendingJob();
  if (!job) {
    return false;
  }

  let outputPath: string | null = null;
  console.log(`[worker] claimed render job ${job.id}`);
  try {
    outputPath = await renderJobVideo(job.id, job.payload);
    const videoUrl = await uploadMp4(outputPath, job.id);
    await markJobCompleted(job.id, videoUrl);
    console.log(`[worker] completed render job ${job.id}: ${videoUrl}`);
  } catch (error) {
    console.error(`[worker] failed render job ${job.id}`, error);
    await markJobFailed(job.id, error);
  } finally {
    if (outputPath) {
      await unlink(outputPath).catch((error) => {
        console.warn(`[worker] failed to delete temp file ${outputPath}`, error);
      });
    }
  }
  return true;
}

async function workerLoop(workerId: number): Promise<void> {
  while (!shuttingDown) {
    try {
      active += 1;
      const processed = await processNextJob();
      active -= 1;
      if (!processed) {
        await sleep(pollIntervalMs);
      }
    } catch (error) {
      active = Math.max(0, active - 1);
      console.error(`[worker:${workerId}] loop error`, error);
      await sleep(pollIntervalMs);
    }
  }
}

async function shutdown(signal: string): Promise<void> {
  console.log(`[worker] received ${signal}, shutting down`);
  shuttingDown = true;
  while (active > 0) {
    await sleep(500);
  }
  await closeDb();
  process.exit(0);
}

process.on("SIGTERM", () => void shutdown("SIGTERM"));
process.on("SIGINT", () => void shutdown("SIGINT"));

async function main(): Promise<void> {
  console.log(`[worker] starting Remotion worker with concurrency=${concurrency}`);
  await ensureRenderJobsTable();
  await Promise.all(Array.from({ length: concurrency }, (_, index) => workerLoop(index + 1)));
}

main().catch(async (error) => {
  console.error("[worker] fatal error", error);
  await closeDb().catch(() => undefined);
  process.exit(1);
});

