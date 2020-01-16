"""
discover

Given

    one site_id
    one site_url

Arguments

    TRY_COUNT = 3?

Local vars

    existing_article_urls: from db (from Article, Article.site_id = site_id)
    empty_count = 0

[selenium]

    enter site_url
    while empty_count < TRY_COUNT: scroll once
        N Fb posts -> N fb_post_urls
        match fb_post_urls with existing_article_urls
        -> M post urls (to be new Articles)
            if M = 0:
                empty_count += 1
            else:
                -> db: create M new Articles
                    Article.url = post url
                    Article.site_id = site_id
                    Article.article_type = FBPost
                    Article.next_snapshot_at = 0
                add M post urls to existing_article_url
"""