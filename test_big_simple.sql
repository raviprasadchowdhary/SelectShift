SELECT
    mr.member_id,
    mr.first_name,
    mr.last_name,
    LENGTH(mr.email_norm) AS email_length,
    INSTR(mr.email_norm, '@') AS at_position,
    mr.date_of_birth,
    CEIL(mcs.claim_avg) AS avg_claims_rounded,
    INITCAP(am.last_name) AS last_name_initcap,
    am.address_line1
FROM
    member_registry mr
    INNER JOIN member_claims_summary mcs ON mr.member_id = mcs.member_id
    LEFT OUTER JOIN address_master am ON mr.member_id = am.member_id
WHERE
    mr.status = 'ACTIVE'
    AND mr.date_of_birth >= DATE '1980-01-01'
ORDER BY
    mr.last_name, mr.first_name
FETCH FIRST 100 ROWS ONLY;
