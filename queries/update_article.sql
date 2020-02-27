-- :name update_article :affected
UPDATE Article
SET
  first_snapshot_at = :first_snapshot_at,
  last_snapshot_at = :last_snapshot_at,
  next_snapshot_at = :next_snapshot_at,
  snapshot_count = :snapshot_count
WHERE
  article_id = :article_id
