from src.bot.Bot import Bot
import networkx as nx
from src.symbols.ObjectSymbols import ObjectSymbols


class MyBot(Bot):

    def __init__(self):
        super().__init__()

    def get_name(self):
        # Find a name for your bot
        return 'My bot'

    def moveTowardsTreasure(self, game_state, character_state, other_bots):

        parsed = self.pathfinder.parse_game_state(game_state)
        graph = self.pathfinder.create_graph(parsed)
        adjDicts = nx.to_dict_of_dicts(graph)

        transitions = adjDicts[character_state['location']]
        transList = list(transitions.keys())

        seen = set()
        seen.update(transList)
        goal = None
        worseGoal = None

        while(transList != []):

            nowExploring = transList.pop()
            seen.add(nowExploring)

            x = nowExploring[0]
            y = nowExploring[1]

            if (parsed[x][y] == ObjectSymbols.JUNK):

                valid = True

                for otherBot in other_bots:

                     if (otherBot['location'] == nowExploring):
                        if (worseGoal is None):
                            worseGoal = nowExploring
                        valid = False

                if valid:

                    goal = nowExploring
                    print("Found material source", nowExploring)
                    break

            newNodes = list(adjDicts[nowExploring].keys())
            newNodes = [node for node in newNodes if node not in seen]

            seen.update(newNodes)

            transList = newNodes + transList

        if (goal is None):
            goal = worseGoal

        direction = self.pathfinder.get_next_direction(character_state['location'], goal)
        return direction

    def nearestDanger(self, game_state, character_state, other_bots):

        parsed = self.pathfinder.parse_game_state(game_state)
        graph = self.pathfinder.create_graph(parsed)
        adjDicts = nx.to_dict_of_dicts(graph)

        transitions = adjDicts[character_state['location']]
        transList = list(transitions.keys())

        seen = set()
        seen.update(transList)
        goal = None

        while(transList != []):

            nowExploring = transList.pop()
            seen.add(nowExploring)

            x = nowExploring[0]
            y = nowExploring[1]

            for otherBot in other_bots:

                if (otherBot['location'] == nowExploring):
                    print("Found nearest danger at", nowExploring)
                    return nowExploring

            newNodes = list(adjDicts[nowExploring].keys())
            newNodes = [node for node in newNodes if node not in seen]

            seen.update(newNodes)

            transList = newNodes + transList

        direction = self.pathfinder.get_next_direction(character_state['location'], goal)
        return direction


    def turn(self, game_state, character_state, other_bots):

        super().turn(game_state, character_state, other_bots)

        parsed = self.pathfinder.parse_game_state(game_state)
        graph = self.pathfinder.create_graph(parsed)

        currentlyCarrying = character_state['carrying']
        currentLocation = character_state['location']
        currentHealth = character_state['health']

        x = currentLocation[0]
        y = currentLocation[1]

        standingOnBase = (currentLocation == character_state['base'])
        standingOnTreasure = (parsed[x][y] == ObjectSymbols.JUNK)
        
        holding = (currentlyCarrying > 0)

        enemyDist = self.nearestDanger(game_state, character_state, other_bots)
        path = nx.astar_path(graph, enemyDist, character_state['location'])
        enemyIsNear = (len(path) < 4)

        if (holding and standingOnBase):
            return self.commands.store()
        if (standingOnBase and currentHealth < 90):
            return self.commands.rest()
        if (not holding and not standingOnTreasure):
            d = self.moveTowardsTreasure(game_state, character_state, other_bots)
            return self.commands.move(d)
        if (standingOnTreasure and enemyIsNear or currentlyCarrying > 500):
            base = character_state['base']
            direction = self.pathfinder.get_next_direction(character_state['location'], base)
            return self.commands.move(direction)
        if (standingOnTreasure and not enemyIsNear):
            return self.commands.collect()
        if (holding):
            base = character_state['base']
            direction = self.pathfinder.get_next_direction(character_state['location'], base)
            return self.commands.move(direction)


