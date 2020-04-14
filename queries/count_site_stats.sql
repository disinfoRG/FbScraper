SELECT 
	site_id, 
    (
    SELECT count(article_id) from Article
    where site_id = A.site_id 
    and created_at >=:time_start and created_at < :time_end
    ) as discover_count,
    (
    SELECT count(article_id) 
    from 
    (Select ArticleSnapshot.article_id, ArticleSnapshot.snapshot_at, Article.site_id
    from Article
    inner join ArticleSnapshot
    on Article.article_id = ArticleSnapshot.article_id
    ) as Sub
    where site_id = A.site_id
    and snapshot_at >=:time_start and snapshot_at < :time_end
    ) as update_count
FROM Article as A
GROUP BY site_id
HAVING discover_count > 0 or update_count > 0;
