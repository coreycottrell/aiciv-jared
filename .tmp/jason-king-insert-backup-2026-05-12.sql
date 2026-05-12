-- Pre-INSERT backup of Couplify household rows + count snapshot
-- Date: 2026-05-12
-- Purpose: rollback reference before Jason King row insert
-- DB: purebrain-clients (aaade55e-f888-48ea-8e63-b934d697379b)

-- Pre-INSERT total count: 65

-- Couplify rows snapshot:
-- id=90  jay@couplify.com     Jay Whitehurst    Spark    Partnered  active   I-P4WNDS799EYY  499
-- id=94  sheila@couplify.com  Sheila Whitehurst Kindred  Partnered  active   I-RBXHJ68JCJPL  499
-- id=95  amy@couplify.com     Amy Housand       Cai      Partnered  covered  ''              0

-- Rollback if needed:
-- DELETE FROM clients WHERE LOWER(email)='jason@couplify.com';
