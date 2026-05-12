import pg from "pg";

const { Pool } = pg;

export interface RenderJob {
  id: string;
  status: "pending" | "processing" | "completed" | "failed";
  payload: RenderPayload;
  video_url: string | null;
  error_message: string | null;
  retry_count: number;
  created_at: Date;
  updated_at: Date;
  completed_at: Date | null;
}

export interface RenderPayload {
  title: string;
  subtitle?: string;
  script: string;
  bullets?: string[];
  brandName?: string;
  cta?: string;
  durationSeconds?: number;
  fps?: number;
}

const databaseUrl = process.env.DATABASE_URL;

if (!databaseUrl) {
  throw new Error("DATABASE_URL is required");
}

export const pool = new Pool({
  connectionString: databaseUrl,
  ssl: databaseUrl.includes("localhost") || databaseUrl.includes("127.0.0.1")
    ? false
    : { rejectUnauthorized: false },
  max: Number(process.env.WORKER_CONCURRENCY ?? "1") + 2,
});

export async function ensureRenderJobsTable(): Promise<void> {
  await pool.query(`
    create table if not exists render_jobs (
      id uuid primary key default gen_random_uuid(),
      status text not null default 'pending',
      payload jsonb not null default '{}'::jsonb,
      video_url text,
      error_message text,
      retry_count integer not null default 0,
      created_at timestamp not null default now(),
      updated_at timestamp not null default now(),
      completed_at timestamp
    );
  `);
  await pool.query(`
    create index if not exists idx_render_jobs_pending
      on render_jobs (created_at)
      where status = 'pending';
  `);
}

export async function claimPendingJob(): Promise<RenderJob | null> {
  const client = await pool.connect();
  try {
    await client.query("begin");
    const result = await client.query<RenderJob>(`
      with next_job as (
        select id
        from render_jobs
        where status = 'pending'
        order by created_at asc
        limit 1
        for update skip locked
      )
      update render_jobs
      set status = 'processing',
          updated_at = now(),
          error_message = null
      where id in (select id from next_job)
      returning *;
    `);
    await client.query("commit");
    return result.rows[0] ?? null;
  } catch (error) {
    await client.query("rollback");
    throw error;
  } finally {
    client.release();
  }
}

export async function markJobCompleted(jobId: string, videoUrl: string): Promise<void> {
  await pool.query(
    `
      update render_jobs
      set status = 'completed',
          video_url = $2,
          error_message = null,
          updated_at = now(),
          completed_at = now()
      where id = $1;
    `,
    [jobId, videoUrl],
  );
}

export async function markJobFailed(jobId: string, error: unknown): Promise<void> {
  const message = error instanceof Error ? error.stack ?? error.message : String(error);
  await pool.query(
    `
      update render_jobs
      set status = 'failed',
          error_message = $2,
          retry_count = retry_count + 1,
          updated_at = now()
      where id = $1;
    `,
    [jobId, message.slice(0, 8000)],
  );
}

export async function closeDb(): Promise<void> {
  await pool.end();
}

