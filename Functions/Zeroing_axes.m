function arrays = Zeroing_axes(arrays)
    for i = 1:numel(arrays)
        min_value = min(min(arrays{i}));

        % Subtract the minimum value from all elements
        arrays{i} = arrays{i} - min_value;
    end
end
