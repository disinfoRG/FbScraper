-- :name get_articles_outdated :many
select * from Article
where
  next_snapshot_at != 0
  and next_snapshot_at < :now
  and article_type="FBPost"
ORDER BY next_snapshot_at ASC
LIMIT :amount