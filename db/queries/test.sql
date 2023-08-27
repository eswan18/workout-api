select ids.id, CASE WHEN workouts.id IS NULL THEN false ELSE true END AS exists
from (values
    ('123e4567-e89b-12d3-a456-426655440000'::uuid), ('a8d26bbc-c6af-4d85-b019-82096b1a21af'::uuid)
) as ids(id)
left join workouts
on workouts.id = ids.id;
