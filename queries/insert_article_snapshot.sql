-- :name insert_article_snapshot :insert
INSERT INTO ArticleSnapshot (article_id, snapshot_at, raw_data)
values (:article_id, :snapshot_at, :raw_data)