
class GuardianAI():

    """ Coded for guardian. """
    def __init__(self):
        self.nextMoves = []

    def decideMove(self, battle):
        if self.nextMoves: return self.nextMoves.pop(0)
        player = battle.players[battle.turn]
        enemy = battle.players[battle.turn - 1]
        if battle.get_ability_status(4) == "Ready": return 4 #Attack
        if battle.get_ability_status(5) == "Ready" and not player.block_next: return 5 #Parry
        if battle.get_ability_status(0) == "Ready":
            return 3 if enemy.x > player.x else 0 # Move Left or Right
        return -1 # No Move Available


def getAI(type):
    return GuardianAI() if type == "guardian" else RangerAI()



class RangerAI():

    def __init__(self):
        self.nextMoves = []

    def decideMove(self, battle):
        if self.nextMoves: return self.nextMoves.pop(0)
        player = battle.players[battle.turn]
        enemy = battle.players[battle.turn - 1]
        if enemy.type == "ranger": return 4 # Attack if enemy is ranger
        if abs(enemy.x - player.x) <= enemy.range: # if enemy in range
            if (player.x == player.MIN_X):
                self.nextMoves += [2, 2] # Do three jumps past enemy
                return 2
            elif player.x == player.MAX_X:
                self.nextMoves += [1, 1] # Do three jumps past enemy
                return 1
            return 0 if enemy.x > player.x else 3 # Else move away
        if battle.get_ability_status(5) == "Ready" and not player.block_next: return 5 # FrostShot
        return 4
