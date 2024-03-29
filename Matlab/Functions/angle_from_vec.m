function angle = angle_from_vec(u,v)
    % Vectorized function returning the signed angle between u and v
    %   along the second dimension
    normal_dir = [0 0 1];

    size_u = size(u);
    size_v = size(v);

    if (size_u(2) < 2 || size_u(2) > 3)  && (size_u(1) == 2 || size_u(1) == 3)
        u = u.';
        size_u = size(u);
    end

    if (size_v(2) < 2 || size_v(2) > 3) && (size_v(1) == 2 || size_v(1) == 3)
        v = v.';
        size_v = size(v);
    end

    % Check that the size of u and v is not <1 or >3
    if size_u(2) < 2 || size_u(2) > 3 || size_v(2) < 2 || size_v(2) > 3
        error('The inputs must be vectors of length 2 or 3 in the second dimension')
    end

    % Add a 0 at the end of the vectors if they are 2D to make them 3D
    % (necessary for using the functions cross...)
    if size_u(2) == 2
        u = [u zeros(size_u(1),1)];
    end

    if size_v(2) == 2
        v = [v zeros(size_v(1),1)];
    end
    
    % Calculate the angle
    cross_val = cross(u,v,2);
    sign_val = sign(cross_val * normal_dir.');
    angle = atan2(sign_val.*vecnorm(cross_val,2,2),dot(u,v,2));
end

