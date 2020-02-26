-- :name get_sites_need_to_discover :many
select * from Site
where
  is_active = 1
  and type = :site_type
  and site_id = :site_id
limit :amount