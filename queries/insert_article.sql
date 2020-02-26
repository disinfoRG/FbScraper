-- :name insert_article :insert
INSERT INTO Article (site_id, url, url_hash, first_snapshot_at, last_snapshot_at, next_snapshot_at, snapshot_count, redirect_to, article_type, created_at)
values (:site_id, :url, :url_hash, :first_snapshot_at, :last_snapshot_at, :next_snapshot_at, :snapshot_count, :redirect_to, :article_type, :created_at)