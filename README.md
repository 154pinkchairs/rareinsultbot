*WIP*

A Reddit bot designed specifically for [https://reddit.com/r/rareinsults](/r/rareinsults) subreddit. Due to the specifics of the images posted there it seeks to find the last line of the images posted there, extract it while filtering the blacklisted characters, lines that are too short etc.
It can be tweaked though to work with other subreddits. 

It is a simpler and more secure alternative to [https://github.com/gregoryneal/ocrbot](ocrbot) as it utilizes environmental variables instead of a relational database.

~~It is activated with /u/rareinsultbot and removes the comment and the insult from the list if there are at least 68% "bad bot" comments or 3 downvotes.~~ posting not yet implemented

In the future the codebase might be migrated to Go since Python doesn't support concurrency.