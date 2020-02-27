select
    Integrated_Site_1.*,
    (select count(ArticleSnapshot.article_id) from ArticleSnapshot, Article, Site where ArticleSnapshot.raw_data<>'' and ArticleSnapshot.article_id=Article.article_id and Article.site_id=Site.site_id and Site.type='fb_page') / (select count(Article.article_id) from Article, Site where  Article.site_id=Site.site_id and Site.type='fb_page') as total_updated_ratio,
    Integrated_Site_1.discovered_count / (select count(Article.article_id) from Article, Site where  Article.site_id=Site.site_id and Site.type='fb_page') as discovered_ratio,
    Integrated_Site_1.updated_count / (select count(ArticleSnapshot.article_id) from ArticleSnapshot, Article, Site where ArticleSnapshot.raw_data<>'' and ArticleSnapshot.article_id=Article.article_id and Article.site_id=Site.site_id and Site.type='fb_page') as updated_ratio,
    sum(Integrated_Site_2.discovered_count) as discovered_cumulated,
    sum(Integrated_Site_2.discovered_count) / (select count(Article.article_id) from Article, Site where  Article.site_id=Site.site_id and Site.type='fb_page') as discovered_cumulated_ratio,
    sum(Integrated_Site_2.updated_count) as updated_cumulated,
    sum(Integrated_Site_2.updated_count) / (select count(ArticleSnapshot.article_id) from ArticleSnapshot, Article, Site where ArticleSnapshot.raw_data<>'' and ArticleSnapshot.article_id=Article.article_id and Article.site_id=Site.site_id and Site.type='fb_page') as updated_cumulated_ratio
from
    (
        select
            Discovered_Site.site_id, 
            Discovered_Site.name,
            Discovered_Site.url,
            Discovered_Site.last_crawl_at,            
            Discovered_Site.discovered_count,
            count(ArticleSnapshot.article_id) as updated_count, 
            (count(ArticleSnapshot.article_id)/Discovered_Site.discovered_count) as self_updated_ratio
        from 
            ArticleSnapshot, 
            Article, 
            (
                select 
                    Site.site_id,
                    Site.name,
                    Site.url,
                    Site.last_crawl_at,
                    count(Article.article_id) as discovered_count 
                from 
                    Article, 
                    Site 
                where 
                    Article.site_id=Site.site_id and 
                    Site.type='fb_page' 
                group by 
                    Site.site_id
            ) as Discovered_Site 
        where 
            ArticleSnapshot.raw_data<>'' and 
            ArticleSnapshot.article_id=Article.article_id and 
            Article.site_id=Discovered_Site.site_id 
        group by
            Discovered_Site.site_id
    ) as Integrated_Site_1,
    (
        select
            Discovered_Site.site_id, 
            Discovered_Site.name,
            Discovered_Site.url,
            Discovered_Site.last_crawl_at,            
            Discovered_Site.discovered_count,
            count(ArticleSnapshot.article_id) as updated_count, 
            (count(ArticleSnapshot.article_id)/Discovered_Site.discovered_count) as self_updated_ratio
        from 
            ArticleSnapshot, 
            Article, 
            (
                select 
                    Site.site_id,
                    Site.name,
                    Site.url,
                    Site.last_crawl_at,
                    count(Article.article_id) as discovered_count 
                from 
                    Article, 
                    Site 
                where 
                    Article.site_id=Site.site_id and 
                    Site.type='fb_page' 
                group by 
                    Site.site_id
            ) as Discovered_Site 
        where 
            ArticleSnapshot.raw_data<>'' and 
            ArticleSnapshot.article_id=Article.article_id and 
            Article.site_id=Discovered_Site.site_id and 
        group by
            Discovered_Site.site_id
    ) as Integrated_Site_2
where
    Integrated_Site_1.discovered_count<=Integrated_Site_2.discovered_count or 
    (
        Integrated_Site_1.discovered_count=Integrated_Site_2.discovered_count and 
        Integrated_Site_1.site_id=Integrated_Site_2.site_id
    )
group by
    Integrated_Site_1.site_id,
    Integrated_Site_1.discovered_count
order by
    Integrated_Site_1.discovered_count desc,
    Integrated_Site_1.site_id desc;