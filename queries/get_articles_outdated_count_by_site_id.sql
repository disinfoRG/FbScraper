-- :name get_articles_outdated_count_by_site_id :many
SELECT count(*) AS count FROM Article
WHERE
  site_id = :site_id
  and next_snapshot_at != 0
  and next_snapshot_at < :now
  and article_type="FBPost"
ORDER BY next_snapshot_at ASC