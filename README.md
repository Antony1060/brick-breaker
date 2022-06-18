# Brick Breaker
A game that originally started as a small school project. Later on I realized that the idea had gread potential to demonstrate how certain algorithms can be used to make the game itself more performant.

## The problem
When I originally started writing this, I wasn't really thinking about performance much. Turns out calculating the collision of 1000 balls with 1260 cubes 60 times a second was not something computers coult do very quickly. So the focus quickly changed to optimizing the hell out of the game.

At this point the time complexity of the frame was `O(n * x * y)` where `n` are number of balls, `x` number of cubes in one row and `y` number of cubes in one column.

## Optimizations
### Limiting the columns
First and probably the most significant optimization was picking only the sorrounding colums of balls around a ball.
This was accomplished by remembering all cubes aligned against any `x` coordinate value and then going through all `x` values within a 10 offset of a ball.
This was we can only grab the cube columns in that range, lowering the time complexity to `O(n * y)`.

#### Further microoptimizations
The before described approach was still going through 30-ish x values even though only a limited amount of them contained anything. This wasn't a big issue but we saw room for improvement.
Adding a small support list which pointed to the next x value which contained something helped.

### Binary search
As mentioned above, time complexity now was `O(n * y)`. Game was now in a playable state but with very noticable slow-downs. Not satisfied.
The algorithm was still handling all of our `y` cubes. Solution was to binary search against all cubes in the same `x` coordinate by their `y` coordinate value and find the first cube closest to the ball by some offset. Then grab all the cubes until their `y` becomes bigger than our ball's `y` + some offset.

This lowered the time complexity to `O(n * log(y))`.

### Going insane
The game was now completely playable, but I wanted more. So after a ton of reasearch on how we can use C code in python. I made a simple C extension module handling all collison logic between a ball and a cube.
This ended up speeding up the computation times by 2x.

## Takeaway
Making this game made me realize that I should probably give game devs a bit more credit... or at least the game engine devs. I can't imagine the sheer amount of optimizations and microoptimizations going into those.

## Credits
Big big thanks to [@VisenP](https://github.com/VisenP) for helping me with this project because personally I would never be able to do this myself.
