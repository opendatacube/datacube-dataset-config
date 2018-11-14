DO $$
DECLARE
    dataset_row RECORD;
BEGIN
FOR dataset_row IN
		SELECT * FROM agdc.dataset where dataset_type_ref = 49
	LOOP
		DELETE FROM agdc.dataset_location
		WHERE agdc.dataset_location.dataset_ref = dataset_row.id;
		DELETE FROM agdc.dataset_source
		WHERE agdc.dataset_source.dataset_ref = dataset_row.id;
	END LOOP;
DELETE FROM agdc.dataset where dataset_type_ref = 49;
DELETE FROM agdc.dataset_type where id = 49;
END;
$$;
