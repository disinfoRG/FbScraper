-- :name get_sites_to_discover :many
select * from Site
ORDER BY last_crawl_at ASC