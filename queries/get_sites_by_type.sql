-- :name get_sites_by_type :many
select * from Site
where
  is_active = 1
  and type = :site_type
limit :amount