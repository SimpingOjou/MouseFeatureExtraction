function [angles] = successive_angles(vectors, ground_vec)
    % Returns the successive angles between the vectors, and one final
    % angle between the last vector and ground_vec
    % the input vectors must be of shape (joint id, frame id, 2) with the
    % last dimension being x (id 1) or y (id 2)

    vec_size = size(vectors);
    angles = zeros(vec_size(1), vec_size(2));

    % Calculate the successive angles
    for i=1:vec_size(1)-1
        angles(i,:) = angle_from_vec(-squeeze(vectors(i,:,:)), squeeze(vectors(i+1,:,:)));
    end
    angles(end,:) = angle_from_vec(-squeeze(vectors(end,:,:)), repmat(ground_vec, vec_size(2), 1));
end

