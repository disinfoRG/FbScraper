-- :name count_articles_discovered_in_interval :many
SELECT site_id, count(*) as discover_count
FROM Article
WHERE
  created_at BETWEEN :time_start AND :time_end
GROUP BY site_id;