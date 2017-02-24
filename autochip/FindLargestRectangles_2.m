function [C, H, W, M] = FindLargestRectangles_2(I, crit, minSize, skip)
% finds largest rectangle regions within all points set to 1.
% input: I       - B/W boolean matrix or output of FindLargestSquares
%        minSize - [height width] - minimum width and height on regions of 
%                  interest (used to restrict final choise)
%        crit    - Optimazation Criteria parameters to optimize:
%                   crit(1)*height + crit(2)*width + crit(3)*height*width
%        skip    - Only check every skipth row/col when looking for large
%                   rectangles
% output: 
%         C    - value of the optimization criteria "crit" calculated for 
%                each pixel 
%         W, H - for each pixel I(r,c) return height and width of the largest 
%                all-white rectangle with its upper-left corner at I(r,c)
%         M    - Mask the largest all-white rectangle of the image




 
if (nargin < 2)
  crit = [1 1 0]; %default to finding largest perimeter rectangle
end
if (nargin < 3)
  minSize = [1 1];
end
if (nargin < 4 || skip < 1) 
  skip = 1;
end


p = crit;
[nR nC] = size(I);
if (minSize(1)<1), minSize(1)= floor(minSize(1)*nR); end
if (minSize(2)<1), minSize(2)= floor(minSize(2)*nC); end
if (max(I(:)) - min(I(:))==1), %if its a B/W matrix
  S = FindLargestSquares(I);
else % if we've already run find largest squares
  S = I;
end
n = max(S(:)); % max square side
W = S; % make a carbon copy of the matrix data
H = S;
C = ((p(1)+p(2)) + p(3)*S) .* S; % p(1)*width + p(2)*height + p(3)*height*width for height=width=S;
d = round((3*n)/4);
minH = max(min(minSize(1), d),1); % either min(input minimum, .75 * max square side)  or  1
minW = max(min(minSize(2), d),1);

%% look for rectangles with width>height
height2width = zeros(n+1,1);  % Store array with largest widths aviable for a given height
for r = 1 : skip : nR               % each row is processed independently
  height2width(:) = 0;        % reset the List
  for c = nC: -1 : 1         % go through all pixels in a row right to left
    s = S(r,c);              % s is a size of the biggest square with its corner at (r,c)
    if (s>0)                 % if pixel I(r,c) is true/white 
      MaxCrit = C(r,c);      % initialize the Max Criteria using square
      for height = s:-1:1     % go through all possible width&height combinations. Start with more likely to be the best
        width = height2width(height); % look up width for a given height
        width = max(width+1,s);
        height2width(height) = width;
        Crit = p(1)*height + p(2)*width + p(3)*width*height;
        if (Crit>MaxCrit),   % check if it produces larger Criteria
          MaxCrit = Crit;    % if it does than save the results
          W(r,c)  = width;
          H(r,c)  = height;
        end % if Crit
      end % for height
      C(r,c)  = MaxCrit;
    end % if s
    height2width((s+1):end) = 0;    % heights>s will not be aviable for the next pixel
  end % for c
end
clear height2width

%% look for rectangles with width<height
width2height = zeros(n+1,1);  % Store array with largest widths aviable for a given height
for c = 1 : skip : nC               % each column is processed independently
  width2height(:) = 0;        % reset the List
  for r = nR: -1 : 1         % go through all pixels in a column bottom to top
    s = S(r,c);              % s is a size of a square with its corner at (r,c)
    if (s>0)                 % if pixel I(r,c) is true
      MaxCrit = C(r,c);      % initialize the Max Criteria using square
      for width = s:-1:1     % go through all possible width&height combinations. Start with more likely to be the best
        height = width2height(width); % look up height for a given width
        height = max(height+1,s);
        width2height(width) = height;
        Crit = p(1)*height + p(2)*width + p(3)*width*height;
        if (Crit>MaxCrit),   % check if it produces larger Criteria
          MaxCrit = Crit;    % if it does than save the results
          W(r,c)  = width;
          H(r,c)  = height;
        end % if Crit
      end % for width
      C(r,c)  = MaxCrit;
    end % if s
    width2height((s+1):end) = 0;    % heights>s will not be aviable for the next pixel
  end % for r
end

%% Create container mask
CC = C;
CC( H<minH | W<minW ) = 0; % first try to obey size restrictions
[~, pos] = max(CC(:));
if (isempty(pos)), [~, pos] = max(C(:)); end % but when it fails than drop them
[r c] = ind2sub(size(C), pos);
M = false(size(C));
M( r:(r+H(r,c)-1), c:(c+W(r,c)-1) ) = 1;
