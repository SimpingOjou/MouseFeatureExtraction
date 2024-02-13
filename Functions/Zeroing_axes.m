function [x_body, y_body, z_body, x_forelimb_L, y_forelimb_L,...
    z_forelimb_L, x_hindlimb_L, y_hindlimb_L, z_hindlimb_L, x_tail,...
    y_tail, z_tail] = Zeroing_axes(x_body, y_body, z_body, x_forelimb_L,...
    y_forelimb_L, z_forelimb_L, x_hindlimb_L, y_hindlimb_L, z_hindlimb_L,...
    x_tail, y_tail, z_tail)

    arrays = {x_body, y_body, z_body, x_forelimb_L,...
    y_forelimb_L, z_forelimb_L, x_hindlimb_L, y_hindlimb_L, z_hindlimb_L,...
    x_tail, y_tail, z_tail};

    for i = 1:numel(arrays)
        min_value = min(min(arrays{i}));

        % Subtract the minimum value from all elements
        arrays{i} = arrays{i} - min_value;
    end

    % Extract arrays
    x_body = arrays{1};
    y_body = arrays{2};
    z_body = arrays{3};
    x_forelimb_L = arrays{4};
    y_forelimb_L = arrays{5};
    z_forelimb_L = arrays{6};
    x_hindlimb_L = arrays{7};
    y_hindlimb_L = arrays{8};
    z_hindlimb_L = arrays{9};
    x_tail = arrays{10};
    y_tail = arrays{11};
    z_tail = arrays{12};
end
