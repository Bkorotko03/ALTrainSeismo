- tres windowing will be inaccurate when using clicker tuned to uno events
- closest approach to cudahy is ~ 170 m, distance from facilities room to cudahy is ~ 260 m
- this is both because speed of sound causes lag (on order of 1 second), and because signal peak at cudahy could be 10-15 seconds before or after the click at the station
- the signal received at cudahy from the station is ~42% what it would be at point of closest approach, we are losing over half our signal!!!
- how do we approach correctly windowing for tres then? some confidence interval type thing?

## ideas:
- if we set some characteristic voltage cutoffs for what we consider the event threshold for tres, we can apply these to create new windowing scheme for tres and then visually check if it lines up roughly with uno
- these windows could deviate again by like 15 seconds potentially
- there also might events heard by uno that are not heard by tres, ie incoming trains going southbound that stop at the station
- 