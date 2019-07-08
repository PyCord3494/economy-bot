import discord
from discord.ext import commands

class TTT(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.grid = []
        self.game_in_progress = False

    @commands.command(description="Play TicTacToe with a friend!", aliases=['ttt'], pass_context=True)
    async def tictactoe(self, ctx, member: discord.Member=None):
        """ Play Tic-Tac-Toe with a friend! """
        channel = ctx.message.channel

        if self.game_in_progress:
            return

        if member is None:
            await channel.send("You must mention an opponent.")
            return

        self.game_in_progress = True
        self.populate_grid()
        author = ctx.message.author
        win = False
        draw = False
        player = "X"
        player_member = author
        board = await self.display_grid(channel)

        while not win and not draw:
            mention = await channel.send("<@" + str(player_member.id) + ">, your turn!")

            def is_me(m):
                return m.author.id == player_member.id

            msg = await self.bot.wait_for('message', check=is_me)

            move = msg.content
            legal = await self.make_move(move, player, channel)

            if legal:
                messages = [board, msg, mention]
                await channel.delete_messages(messages)
                board = await self.display_grid(channel)
                win = self.check_win()

                if not win:
                    draw = self.check_draw()
                    player = "O" if player == "X" else "X"
                    player_member = member if player_member == author else author

        await channel.send("------ <@" + str(player_member.id) + "> wins! ------") if not draw else await channel.send("------ Draw! ------")
        self.game_in_progress = False
            

    async def display_grid(self, channel):
        string = ""
        for row in self.grid:
            for n in row:
                string += ("   {}   ".format(n))

            string += "\n"
        
        msg = await channel.send("```autohotkey\r{}```\r".format(string))
        return msg

    def populate_grid(self):
        self.grid = []
        n = 1
        for i in range(3):
            self.grid.append([])
            for j in range(3):
                self.grid[i].append(str(n))
                n += 1

    async def make_move(self, move, player, channel):
        for row in self.grid:
            for i, n in enumerate(row):
                if n == move:
                    row[i] = player
                    return True
    
        await channel.send("Illegal move, try again.")
        return False

    def check_win(self):
        # Check for horizontal win
        for row in self.grid:
            if len(set(row)) == 1:
                return True

        # Check for vertical win
        for i in range(3):
            vertical = []
            for row in self.grid:
                vertical.append(row[i])
            if len(set(vertical)) == 1:
                return True

        # Check for diagonal win
        diagonal = []
        diagonal_reverse = []
        for i, row in enumerate(self.grid):
            reverse = row[::-1]
            diagonal.append(row[i])
            diagonal_reverse.append(reverse[i])

        if len(set(diagonal)) == 1 or len(set(diagonal_reverse)) == 1:
            return True

        return False

    def check_draw(self):
        players = ["X", "O"]

        for row in self.grid:
            for el in row:
                if el not in players:
                    return False

        return True

def setup(bot):
    bot.add_cog(TTT(bot))