from typing import Optional
from mcpi_tetris.core.basic import Block, Color, Position
from mcpi_tetris.core.display import DisplayAdapter
from mcpi.minecraft import Minecraft
from mcpi.vec3 import Vec3
from mcpi.block import AIR, WOOL


class McpiDisplayAdapter(DisplayAdapter):

    display_pos: Vec3
    """디스플레이의 기준이 되는 좌표"""

    minecraft: Minecraft
    """마인크래프트 인스턴스"""

    player_id: int
    """테트리스를 조작하는 플레이어의 엔티티 ID"""

    def __init__(self, minecraft: Minecraft, player_id: int = None):
        self.minecraft = minecraft

        if player_id is None:
            player_id = self.minecraft.getPlayerEntityIds()[0]
        
        self.player_id = player_id

    def initialize(self):
        pos = self.minecraft.entity.getPos(self.player_id)

        # XXXXXX
        # X    X
        # X    X
        # X    X
        # XO   X
        # XXXXXX
        #  ↑ Here
        pos.x -= self.width // 2
        pos.z -= 20

        self.display_pos = pos

        # make frame
        for y in [-1, self.height]:
            for x in range(-1, self.width + 1):
                self.minecraft.setBlock(pos.x + x, pos.y + y, pos.z, WOOL.id, 15) # WOOL (Black)

        for x in [-1, self.width]:
            for y in range(-1, self.height + 1):
                self.minecraft.setBlock(pos.x + x, pos.y + y, pos.z, WOOL.id, 15) # WOOL (Black)

    def get_wool_color(self, color: Color) -> int:
        """테트리스 Color를 마인크래프트 양털 컬러로 변환"""

        if color == Color.LIGHT_BLUE:
            return 3
        elif color == Color.DARK_BLUE:
            return 11
        elif color == Color.ORANGE:
            return 1
        elif color == Color.YELLOW:
            return 4
        elif color == Color.GREEN:
            return 13
        elif color == Color.RED:
            return 14
        elif color == Color.MAGENTA:
            return 2
        
        return 0 # fallback color is white

    def onblockchange(self, position: Position, block: Optional[Block]):
        pos = self.display_pos

        if block is None:
            self.minecraft.setBlock(pos.x + position.x, pos.y + position.y, pos.z, AIR.id)
        else:
            self.minecraft.setBlock(pos.x + position.x, pos.y + position.y, pos.z, WOOL.id, self.get_wool_color(block.color))
    
    def ongameover(self):
        pos = self.display_pos

        for y in range(self.height):
            for x in range(self.width):
                if self.minecraft.getBlock(pos.x + x, pos.y + y, pos.z) == WOOL.id:
                    self.minecraft.setBlock(pos.x + x, pos.y + y, pos.z, WOOL.id, 7) # WOOL (grey)

    def close(self):
        pos = self.display_pos

        for y in range(-1, self.height + 1):
            for x in range(-1, self.width + 1):
                self.minecraft.setBlock(pos.x + x, pos.y + y, pos.z, AIR.id)
