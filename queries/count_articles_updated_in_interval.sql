-- :name count_articles_updated_in_interval :many
SELECT site_id, count(*) as update_count
FROM Article
WHERE
  last_snapshot_at BETWEEN :time_start AND :time_end
GROUP BY site_id;