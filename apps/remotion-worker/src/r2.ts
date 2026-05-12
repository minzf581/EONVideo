import { PutObjectCommand, S3Client } from "@aws-sdk/client-s3";
import { createReadStream } from "node:fs";
import { stat } from "node:fs/promises";
import path from "node:path";

function required(name: string): string {
  const value = process.env[name];
  if (!value) {
    throw new Error(`${name} is required`);
  }
  return value;
}

const accountId = required("R2_ACCOUNT_ID");
const accessKeyId = required("R2_ACCESS_KEY_ID");
const secretAccessKey = required("R2_SECRET_ACCESS_KEY");
const bucket = required("R2_BUCKET");
const publicBaseUrl = required("R2_PUBLIC_BASE_URL").replace(/\/$/, "");

const client = new S3Client({
  region: "auto",
  endpoint: `https://${accountId}.r2.cloudflarestorage.com`,
  credentials: {
    accessKeyId,
    secretAccessKey,
  },
});

export async function uploadMp4(filePath: string, jobId: string): Promise<string> {
  const fileStat = await stat(filePath);
  const key = `renders/${jobId}/${path.basename(filePath)}`;
  await client.send(
    new PutObjectCommand({
      Bucket: bucket,
      Key: key,
      Body: createReadStream(filePath),
      ContentType: "video/mp4",
      ContentLength: fileStat.size,
      CacheControl: "public, max-age=31536000, immutable",
    }),
  );
  return `${publicBaseUrl}/${key}`;
}

