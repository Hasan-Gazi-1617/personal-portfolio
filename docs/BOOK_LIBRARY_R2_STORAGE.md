# Book Library media storage: Cloudflare R2

The Book model stores its cover, five-page preview, and full PDF through Django's default file storage. Configure Cloudflare R2 as that storage so uploads survive Render deploys and restarts.

## 1. Create an R2 bucket

1. Open the Cloudflare dashboard and go to **R2 Object Storage**.
2. Create a bucket (for example, `hasan-book-library`).
3. Open **Manage R2 API Tokens** and create an API token with **Object Read & Write** permission scoped to this bucket.
4. Copy the Access Key ID and Secret Access Key when shown. The secret is shown only once.
5. Copy the S3 API endpoint shown for the account. It has this format: `https://<ACCOUNT_ID>.r2.cloudflarestorage.com`.

Keep the bucket private. This app generates time-limited signed URLs for cover images and previews, and serves the full PDF through its payment-approved download view.

## 2. Add Render environment variables

In the Render web service, add these variables:

- `R2_ACCESS_KEY_ID`: the R2 token Access Key ID
- `R2_SECRET_ACCESS_KEY`: the R2 token Secret Access Key
- `R2_BUCKET_NAME`: the exact bucket name
- `R2_ENDPOINT_URL`: the account's S3 API endpoint

Do not add the R2 secret to GitHub or paste it into chat. All four variables are required. If none are set, local development uses the filesystem. If only some are set, Django stops with a configuration error instead of silently storing files locally.

## 3. Deploy and verify

Merge the storage change and wait for Render to deploy. Then upload a new test cover image and preview PDF in Django Admin. Open the public Library page and confirm the cover appears; open the book page and test the preview.

Existing files uploaded before R2 is configured remain on the old Render filesystem and are not copied automatically. Download those files from the current deployment/admin environment if still available, then upload them again after R2 is active.

## Notes

- No database migration is required for this storage change.
- The bucket remains private; do not enable public access for full PDFs.
- Render's filesystem is ephemeral, so R2 should be configured before uploading production book files.
