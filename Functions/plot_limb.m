function [] = plot_limb(vectors, center_around_joint_id, angles)
    % Function adding the successive vectors and their corresponding angles
    %   to plot, with the joint center_around_joint_id at (0,0)
    % If no angle is provided (angles=[]), the function simply add the
    %   vectors to the plot

    r=0.2;

    % Calculate the starting position to place the joint
    %   center_around_joint_id at (0,0)
    start_pos = -sum(vectors(1:center_around_joint_id,:), 1);
    
    % calculate the successive positions of the joints by adding the
    %   vectors
    successive_pos = cumsum(vectors);
    joint_pos = [start_pos; start_pos+successive_pos(1:end,:)];

    % Plot the joints and the links between them
    hold on
    plot(joint_pos(:,1),joint_pos(:,2))

    % If angles are provided, plot them
    if ~isempty(angles)
        % Calculate the angles to plot by adding a phase so that the
        %   plotted angle starts at the vector it represents
        th_unit = linspace(0,1);
        vectors_size = size(vectors);
        thetas = -vec_angle(-vectors, repmat([1 0], vectors_size(1), 1)) + th_unit.*angles;
    
        % Cartesian coordinates of the fraction of circle representing the
        %   angle
        xx = joint_pos(2:end,1) + r*cos(thetas);
        yy = joint_pos(2:end,2) + r*sin(thetas);

        plot(xx.',yy.')
    end
end

