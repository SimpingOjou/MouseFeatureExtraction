function [vectors] = get_vectors_from_pos(pos_x,pos_y)
    % Calculate the vectors corresponding to the difference of the
    %   successive positions (along the second dimension)

    vectors_x = pos_x(:,2:end) - pos_x(:,1:end-1);
    vectors_y = pos_y(:,2:end) - pos_y(:,1:end-1);
    
    vectors = cat(3,vectors_x.',vectors_y.');
end

