import React, { useEffect, useState } from 'react';

const BOARD_SIZE = 12; // Square board
const REFRESH_RATE = 75; // ms - faster

// Standard Tetris pieces (tetrominos)
const TETROMINOS = [
  {
    piece: [
      [1, 1, 1, 1], // I piece
    ],
    width: 4,
  },
  {
    piece: [
      [1, 1],
      [1, 1], // O piece (square)
    ],
    width: 2,
  },
  {
    piece: [
      [0, 1, 0],
      [1, 1, 1], // T piece
    ],
    width: 3,
  },
  {
    piece: [
      [0, 1, 1],
      [1, 1, 0], // S piece
    ],
    width: 3,
  },
  {
    piece: [
      [1, 1, 0],
      [0, 1, 1], // Z piece
    ],
    width: 3,
  },
  {
    piece: [
      [1, 0, 0],
      [1, 1, 1], // J piece
    ],
    width: 3,
  },
  {
    piece: [
      [0, 0, 1],
      [1, 1, 1], // L piece
    ],
    width: 3,
  },
];

const LoadingState = ({ isConnected }) => {
  const [board, setBoard] = useState(
    Array(BOARD_SIZE)
      .fill()
      .map(() => Array(BOARD_SIZE).fill(0))
  );
  const [currentPiece, setCurrentPiece] = useState(null);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [sequenceIndex, setSequenceIndex] = useState(0);
  const [shouldClear, setShouldClear] = useState(false);
  const [dots, setDots] = useState('');

  // Animate the loading dots
  useEffect(() => {
    const dotsInterval = setInterval(() => {
      setDots((prev) => (prev.length >= 3 ? '' : prev + '.'));
    }, 500);

    return () => clearInterval(dotsInterval);
  }, []);

  // Get random piece and position
  const getRandomPiece = () => {
    const pieceInfo = TETROMINOS[Math.floor(Math.random() * TETROMINOS.length)];
    const maxX = BOARD_SIZE - pieceInfo.width;
    const startX = Math.floor(Math.random() * maxX);
    return { ...pieceInfo, startX };
  };

  // Check if a piece can be placed at the given position
  const canPlace = (piece, posX, posY) => {
    for (let y = 0; y < piece.length; y++) {
      for (let x = 0; x < piece[y].length; x++) {
        if (piece[y][x]) {
          const boardY = posY + y;
          const boardX = posX + x;
          if (
            boardY >= BOARD_SIZE || // Bottom collision
            boardX < 0 || // Left wall
            boardX >= BOARD_SIZE || // Right wall
            (boardY >= 0 && board[boardY][boardX]) // Piece collision
          ) {
            return false;
          }
        }
      }
    }
    return true;
  };

  // Place the current piece on the board
  const placePiece = () => {
    const newBoard = board.map((row) => [...row]);
    for (let y = 0; y < currentPiece.length; y++) {
      for (let x = 0; x < currentPiece[y].length; x++) {
        if (currentPiece[y][x]) {
          const boardY = position.y + y;
          if (boardY >= 0) {
            newBoard[boardY][position.x + x] = 1;
          }
        }
      }
    }
    setBoard(newBoard);
    return newBoard;
  };

  // Find the lowest possible position for the current piece
  const findLowestPosition = (piece, startX) => {
    let y = 0;
    while (canPlace(piece, startX, y + 1)) {
      y++;
    }
    return y;
  };

  // Start next piece
  const nextPiece = () => {
    const { piece, startX } = getRandomPiece();
    setCurrentPiece(piece);
    setPosition({ x: startX, y: 0 });
    setSequenceIndex((prev) => prev + 1);
  };

  // Game loop
  useEffect(() => {
    if (shouldClear) {
      const timer = setTimeout(() => {
        setBoard(
          Array(BOARD_SIZE)
            .fill()
            .map(() => Array(BOARD_SIZE).fill(0))
        );
        setShouldClear(false);
        nextPiece();
      }, REFRESH_RATE * 2);
      return () => clearTimeout(timer);
    }

    if (!currentPiece) {
      nextPiece();
      return;
    }

    const timer = setInterval(() => {
      const nextY = position.y + 1;

      if (canPlace(currentPiece, position.x, nextY)) {
        setPosition((prev) => ({ ...prev, y: nextY }));
      } else {
        placePiece();
        // Clear board after several pieces have been placed
        if (sequenceIndex > 5 && Math.random() < 0.3) {
          setShouldClear(true);
        } else {
          nextPiece();
        }
      }
    }, REFRESH_RATE);

    return () => clearInterval(timer);
  }, [currentPiece, position, sequenceIndex, shouldClear, board]);

  return (
    <div className="loading-container">
      <div className="loading-content">
        <div className="tetris-board">
          {board.map((row, y) => (
            <div key={y} className="tetris-row">
              {row.map((cell, x) => {
                let isCurrent = false;
                if (currentPiece) {
                  const pieceY = y - position.y;
                  const pieceX = x - position.x;
                  if (
                    pieceY >= 0 &&
                    pieceY < currentPiece.length &&
                    pieceX >= 0 &&
                    pieceX < currentPiece[pieceY].length
                  ) {
                    isCurrent = currentPiece[pieceY][pieceX] === 1;
                  }
                }
                return (
                  <div
                    key={x}
                    className={`tetris-cell ${cell || isCurrent ? 'tetris-cell-filled' : ''}`}
                  />
                );
              })}
            </div>
          ))}
        </div>
        <p className="loading-text text-xs">
          {isConnected ? `Loading${dots}` : `Connecting${dots}`}
        </p>
      </div>
    </div>
  );
};

export default LoadingState;
