# Pokemon Dataset Schema

This document describes the fields available in the Pokemon dataset.

## Basic Information

| Field          | Description                                                     |
| -------------- | --------------------------------------------------------------- |
| name           | The English name of the Pokemon                                 |
| japanese_name  | The Japanese name of the Pokemon                                |
| pokedex_number | The Pokemon's number in the National Pokedex                    |
| generation     | Which generation the Pokemon was introduced in (1-8)            |
| is_legendary   | Boolean indicating if the Pokemon is considered legendary       |
| classfication  | The Pokemon's classification or category (e.g., "Seed Pokemon") |

## Physical Attributes

| Field           | Description                                                  |
| --------------- | ------------------------------------------------------------ |
| height_m        | Height in meters                                             |
| weight_kg       | Weight in kilograms                                          |
| percentage_male | Percentage of the species that is male (some are genderless) |

## Types

| Field | Description                                  |
| ----- | -------------------------------------------- |
| type1 | Primary type of the Pokemon                  |
| type2 | Secondary type of the Pokemon (may be empty) |

## Base Stats

| Field      | Description               |
| ---------- | ------------------------- |
| hp         | Base HP (Hit Points) stat |
| attack     | Base Attack stat          |
| defense    | Base Defense stat         |
| sp_attack  | Base Special Attack stat  |
| sp_defense | Base Special Defense stat |
| speed      | Base Speed stat           |
| base_total | Sum of all base stats     |

## Type Effectiveness

These fields represent the defensive type effectiveness against incoming attacks of each type:

| Field            | Description                                                                       |
| ---------------- | --------------------------------------------------------------------------------- |
| against_bug      | Effectiveness of Bug-type moves against this Pokémon (0.25, 0.5, 1, 2, or 4)      |
| against_dark     | Effectiveness of Dark-type moves against this Pokémon (0.25, 0.5, 1, 2, or 4)     |
| against_dragon   | Effectiveness of Dragon-type moves against this Pokémon (0.25, 0.5, 1, 2, or 4)   |
| against_electric | Effectiveness of Electric-type moves against this Pokémon (0.25, 0.5, 1, 2, or 4) |
| against_fairy    | Effectiveness of Fairy-type moves against this Pokémon (0.25, 0.5, 1, 2, or 4)    |
| against_fight    | Effectiveness of Fighting-type moves against this Pokémon (0.25, 0.5, 1, 2, or 4) |
| against_fire     | Effectiveness of Fire-type moves against this Pokémon (0.25, 0.5, 1, 2, or 4)     |
| against_flying   | Effectiveness of Flying-type moves against this Pokémon (0.25, 0.5, 1, 2, or 4)   |
| against_ghost    | Effectiveness of Ghost-type moves against this Pokémon (0.25, 0.5, 1, 2, or 4)    |
| against_grass    | Effectiveness of Grass-type moves against this Pokémon (0.25, 0.5, 1, 2, or 4)    |
| against_ground   | Effectiveness of Ground-type moves against this Pokémon (0.25, 0.5, 1, 2, or 4)   |
| against_ice      | Effectiveness of Ice-type moves against this Pokémon (0.25, 0.5, 1, 2, or 4)      |
| against_normal   | Effectiveness of Normal-type moves against this Pokémon (0.25, 0.5, 1, 2, or 4)   |
| against_poison   | Effectiveness of Poison-type moves against this Pokémon (0.25, 0.5, 1, 2, or 4)   |
| against_psychic  | Effectiveness of Psychic-type moves against this Pokémon (0.25, 0.5, 1, 2, or 4)  |
| against_rock     | Effectiveness of Rock-type moves against this Pokémon (0.25, 0.5, 1, 2, or 4)     |
| against_steel    | Effectiveness of Steel-type moves against this Pokémon (0.25, 0.5, 1, 2, or 4)    |
| against_water    | Effectiveness of Water-type moves against this Pokémon (0.25, 0.5, 1, 2, or 4)    |

_Note: Values less than 1 indicate resistance (0.5 = "not very effective", 0.25 = doubly resistant),
values greater than 1 indicate vulnerability (2 = "super effective", 4 = doubly vulnerable),
and 0 indicates immunity._

## Other Attributes

| Field             | Description                                              |
| ----------------- | -------------------------------------------------------- |
| abilities         | Pokemon's possible abilities                             |
| base_egg_steps    | Number of steps required to hatch an egg of this Pokemon |
| base_happiness    | Base happiness value when caught                         |
| capture_rate      | How easy the Pokemon is to catch (higher = easier)       |
| experience_growth | The rate at which the Pokemon gains experience           |
