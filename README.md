# PDWorld AI Group Project

PDWorld is an environment where an agent moves between pickup and dropoff locations to deliver items. The agent uses reinforcement learning to determine appropriate operators for each state. 

## Environment
PDWorld is an environment which contains an agent, and together they constitute a state. To initialize the environment, create an environment instance using `PDWorld = environment()`. This will automatically set the pickup and dropoff cells with 8 blocks in each pickup cell and 0 blocks in each dropoff cell, a Q-Table containing the utilities of each operator in every state, and construct an agent which can be referenced using `PDWorld.bot`.

## Agent
Agents execute operators on the environment, and in doing so change the state. The `bot` agent has a state which can be referenced using `PDWorld.bot.currentState`. Agents also have a `bankAccount` attribute that represent the cumulative total reward over the course of each epoch.

Agents act using a policy that is set with the `setPolicy` function. These policies determine the action that the agent takes. The policies are invoked in the `agent.step` function, which updates the current state and the utility of the chosen operator in the Q-Table.

## State
The state class defines the relevant parameters for the agent and environment, keeping track of pickup and dropoff capacities as well as the agent's position. The state class also has a method `hashState` to index the Q-Table given these values.