-- :name get_article_urls_of_site :many
select url from Article
where
  site_id = :site_id