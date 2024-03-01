function [] = plot_points_and_angles(points_x, points_y, angles)
    % Input:
    %   -points_x and points_y are cell arrays where each cell corresponds
    % to a limb, and contains an array of shape (joint id, x or y) corresponding
    % to the successive positions of the joint of the limb
    %   - angle is a cell array where each cell contains a 1D
    % array with all the angles of the joints of the corresponding limb
    % If angle = [], the angles are calculated
    % 
    % Output: No output but the points and corresponding angles are added
    % to the current plot

    % Create the cell arrays of positions and vectors between joints
    size_points = size(points_x);
    positions = cell(size_points(1),1);
    vectors = cell(size_points(1),1);
    for i=1:size_points(1)
        positions{i} = [points_x{i}; points_y{i}].';
        vectors{i} = get_vectors_from_pos(points_x{i}, points_y{i});
    end

    % If angles are not provided, calculate them
    if isempty(angles)
        angles = cell(size_points(1),1);
        for i=1:size_points(1)
            % Vector corresponding to the ground direction, opposite to the movement
            ground_vec = [-1 0];
            
            % Get the angles on each limb (in rad)
            angles{i} = successive_angles(vectors{i}, ground_vec);
        end
    end

    % Plot the limbs and corresponding angles
    for i=1:size_points(1)
        plot_limb(squeeze(vectors{i}), positions{i}(1,:), angles{i})
    end
end

