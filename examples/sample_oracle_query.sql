-- Example Oracle SELECT query for testing
-- This file demonstrates various Oracle-specific syntax

SELECT 
    e.employee_id,
    NVL(e.first_name, 'N/A') || ' ' || NVL(e.last_name, 'N/A') AS full_name,
    DECODE(e.status, 
        'A', 'Active',
        'I', 'Inactive', 
        'T', 'Terminated',
        'Unknown') AS employment_status,
    DECODE(e.department_id,
        10, 'Sales',
        20, 'Engineering',
        30, 'HR',
        'Other') AS department_name,
    TRUNC(e.hire_date) AS hire_date_only,
    TRUNC(SYSDATE) - TRUNC(e.hire_date) AS days_employed,
    NVL(e.salary, 0) AS salary,
    NVL(e.commission_pct, 0) * 100 AS commission_percentage
FROM 
    employees e
WHERE 
    TRUNC(e.hire_date) >= TRUNC(SYSDATE) - 365
    AND e.status IN ('A', 'I')
    AND ROWNUM <= 100
ORDER BY 
    e.hire_date DESC, 
    e.employee_id;
