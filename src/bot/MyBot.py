from src.bot.Bot import Bot
import networkx as nx
from src.symbols.ObjectSymbols import ObjectSymbols
from src.utils.Pathfinder import Pathfinder


class MyBot(Bot):

    def __init__(self):
        super().__init__()

    def get_name(self):
        # Find a name for your bot
        return 'UNIVERSITY ROCHESTER TEAM BEE GREATEST BOT VICTORY TEAM YES'

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


    def existsAPerson(self, game_state, character_state, other_bots, d):

        currentLocation = character_state['location']
        if (d == 'S'):
            attemptedMove = (currentLocation[0] + 1, currentLocation[1])
        elif (d == 'W'):
            attemptedMove = (currentLocation[0], currentLocation[1] - 1)
        elif (d == 'E'):
            attemptedMove = (currentLocation[0], currentLocation[1] + 1)
        else:
            attemptedMove = (currentLocation[0] - 1, currentLocation[1])

        for bot in other_bots:

            botLoc = bot['location']
            if (botLoc == attemptedMove):
                return bot

        return None

    def shouldAttack(self, game_state, character_state, other_bots):

        for direction in ['N', 'W', 'E', 'S']:
            possibleBot = self.existsAPerson(game_state, character_state, other_bots, direction)
            if (possibleBot and possibleBot['health'] <= 10):
                return direction

        return None

    def getBaseDirection(self, game_state, character_state, other_bots, spikesToWalls):

        p = Pathfinder()

        if spikesToWalls:
            game_state = game_state.replace("S", "1")

        p.set_game_state(game_state, other_bots)

        base = character_state['base']
        currentLoc = character_state['location']
        direction = p.get_next_direction(currentLoc, base)
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

        enemyLoc = self.nearestDanger(game_state, character_state, other_bots)
        path = nx.astar_path(graph, enemyLoc, character_state['location'])
        enemyIsNear = (len(path) < 4)
        possibleAttackDirection = self.shouldAttack(game_state, character_state, other_bots)

        try:

            if (holding and standingOnBase):
                return self.commands.store()
            if (standingOnBase and currentHealth < 90):
                return self.commands.rest()
            if (possibleAttackDirection):
                return self.commands.attack(possibleAttackDirection)
            if (currentHealth < 16 and holding and not standingOnTreasure):
                return self.commands.move(self.getBaseDirection(game_state, character_state, other_bots, True))
            if (not holding and not standingOnTreasure):
                direc = self.moveTowardsTreasure(game_state, character_state, other_bots)
                if self.existsAPerson(game_state, character_state, other_bots, direc):
                    return self.commands.attack(direc)
                else:
                    return self.commands.move(direc)
            if (standingOnTreasure and enemyIsNear or currentlyCarrying > 500):
                return self.commands.move(self.getBaseDirection(game_state, character_state, other_bots, False))
            if (standingOnTreasure and not enemyIsNear):
                return self.commands.collect()
            if (holding):
                return self.commands.move(self.getBaseDirection(game_state, character_state, other_bots, False))
            
            return self.commands.idle()

        except:
            return self.commands.idle()


        




