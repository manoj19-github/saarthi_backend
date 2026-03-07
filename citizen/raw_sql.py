
def citizen_details_query(citizen_id):
    query = f"""
    SELECT
        c.id as citizen_id,
        c.first_name,
        c.middle_name,
        c.last_name,
        c.user_type,
        dl2.domain_value as citizen_user_type,
        c.gender,
        dl.domain_value as citizen_gender,
        c.date_of_birth as citizen_date_of_birth,
        c.mobile_number,
        c.email,
        c.status,
        c.state_id,
        sm.state_name,
        c.district_id,
        dm.district_name,
        c.block_id,
        bm.block_name,
        c.created_by,
        c.created_on,
        c.updated_by,
        c.updated_on
        from citizen c
        left join domain_lookup dl on dl.domain_code = c.gender::integer and dl.domain_type='gender'
        left join domain_lookup dl2 on dl2.domain_code = c.user_type::integer and dl2.domain_type = 'user_type'
        left join state_master sm on sm.id = c.state_id  and sm.status=1 
        left join district_master dm on dm.id = c.district_id and dm.status=1
        left join block_master bm on bm.id = c.block_id and bm.status=1
        where c.id = {citizen_id}
        """
    return query