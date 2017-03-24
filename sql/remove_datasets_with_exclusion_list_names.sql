DO $$
DECLARE
    dataset_row RECORD;
BEGIN
FOR dataset_row IN
		SELECT * FROM agdc.dataset where dataset_type_ref IN(SELECT id FROM agdc.dataset_type WHERE name NOT IN ('ls7_ledaps_scene', 'ls8_ledaps_scene', 's1a_gamma0_scene', 'ls7_ledaps_vietnam', 'ls8_ledaps_vietnam', 's1a_gamma0_vietnam'))
	LOOP
		DELETE FROM agdc.dataset_location
		WHERE agdc.dataset_location.dataset_ref = dataset_row.id;
		DELETE FROM agdc.dataset_source
		WHERE agdc.dataset_source.dataset_ref = dataset_row.id;
	END LOOP;
DELETE FROM agdc.dataset where dataset_type_ref IN(SELECT id FROM agdc.dataset_type WHERE name NOT IN ('ls7_ledaps_scene', 'ls8_ledaps_scene', 's1a_gamma0_scene', 'ls7_ledaps_vietnam', 'ls8_ledaps_vietnam', 's1a_gamma0_vietnam'));
DELETE FROM agdc.dataset_type where id IN(SELECT id FROM agdc.dataset_type WHERE name NOT IN ('ls7_ledaps_scene', 'ls8_ledaps_scene', 's1a_gamma0_scene', 'ls7_ledaps_vietnam', 'ls8_ledaps_vietnam', 's1a_gamma0_vietnam'));
END;
$$;