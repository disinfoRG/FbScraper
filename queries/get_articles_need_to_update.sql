-- :name get_articles_need_to_update :many
select * from Article
where
  site_id = :site_id
  and next_snapshot_at != 0
  and next_snapshot_at < :now
  and article_type="FBPost"
ORDER BY next_snapshot_at ASC
LIMIT :amount