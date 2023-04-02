/**
Advantage 360 Key Layout and Aliases

Key Numbers:
╭────┬────┬────┬────┬────┬────┬────╮                                           ╭────┬────┬────┬────┬────┬────┬────╮
   0    1    2    3    4    5    6                                                7    8    9   10   11   12   13
├────┼────┼────┼────┼────┼────┼────┤                                           ├────┼────┼────┼────┼────┼────┼────┤
  14   15   16   17   18   19   20                                               21   22   23   24   25   26   27
├────┼────┼────┼────┼────┼────┼────┤         ╭────┬────╮   ╭────┬────╮         ├────┼────┼────┼────┼────┼────┼────┤
  28   29   30   31   32   33   34             35   36       37   38             39   40   41   42   43   44   45
├────┼────┼────┼────┼────┼────┼────╯    ╭────┼────┼────┤   ├────┼────┼────╮    ╰────┼────┼────┼────┼────┼────┼────┤
  46   47   48   49   50   51                       54       57                       60   61   62   63   64   65
├────┼────┼────┼────┼────┼────╯                   ├────┤   ├────┤                   ╰────┼────┼────┼────┼────┼────┤
  66   67   68   69   70                  71   72   73       74   75   76                  77   78   79   80   81
╰────┴────┴────┴────┴────╯              ╰────┴────┴────╯   ╰────┴────┴────╯              ╰────┴────┴────┴────┴────╯

Key Aliases:
╭─────┬─────┬─────┬─────┬─────┬─────┬─────╮                                   ╭─────┬─────┬─────┬─────┬─────┬─────┬─────╮
  L06   L05   L04   L03   L02   L01   L00                                       R00   R01   R02   R03   R04   R05   R06
├─────┼─────┼─────┼─────┼─────┼─────┼─────┤                                   ├─────┼─────┼─────┼─────┼─────┼─────┼─────┤
  L16   L15   L14   L13   L12   L11   L10                                       R10   R11   R12   R13   R14   R15   R16
├─────┼─────┼─────┼─────┼─────┼─────┼─────┤      ╭────┬────╮ ╭────┬────╮      ├─────┼─────┼─────┼─────┼─────┼─────┼─────┤
  L26   L25   L24   L23   L22   L21   L20         LT01 LT00   RT00 RT01         R20   R21   R22   R23   R24   R25   R26
├─────┼─────┼─────┼─────┼─────┼─────┼─────╯ ╭────┼────┼────┤ ├────┼────┼────╮ ╰─────┼─────┼─────┼─────┼─────┼─────┼─────┤
  L35   L34   L33   L32   L31   L30                    LT10   RT10                    R30   R31   R32   R33   R34   R35
├─────┼─────┼─────┼─────┼─────┼─────╯                 ├────┤ ├────┤                 ╰─────┼─────┼─────┼─────┼─────┼─────┤
  L44   L43   L42   L41   L40                LT22 LT21 LT20   RT20 RT21 RT22                R40   R41   R42   R43   R44
╰─────┴─────┴─────┴─────┴─────╯             ╰────┴────┴────╯ ╰────┴────┴────╯             ╰─────┴─────┴─────┴─────┴─────╯
*/
       
#pragma once

/**
 * Left Hand
 */
#define L06  0
#define L05  1
#define L04  2
#define L03  3
#define L02  4
#define L01  5
#define L00  6

#define L16 14
#define L15 15
#define L14 16
#define L13 17
#define L12 18
#define L11 19
#define L10 20

#define L26 28
#define L25 29
#define L24 30
#define L23 31
#define L22 32
#define L21 33
#define L20 34

#define L35 46
#define L34 47
#define L33 48
#define L32 49
#define L31 50
#define L30 51

#define L44 66
#define L43 67
#define L42 68
#define L41 69
#define L40 70

/**
 * Right Hand
 */
#define R00  7
#define R01  8
#define R02  9
#define R03 10
#define R04 11
#define R05 12
#define R06 13

#define R10 21
#define R11 22
#define R12 23
#define R13 24
#define R14 25
#define R15 26
#define R16 27

#define R20 39
#define R21 40
#define R22 41
#define R23 42
#define R24 43
#define R25 44
#define R26 45

#define R30 60
#define R31 61
#define R32 62
#define R33 63
#define R34 64
#define R35 65

#define R40 77
#define R41 78
#define R42 79
#define R43 80
#define R44 81

/**
 * Left Thumb
 */
#define LT01 35
#define LT00 36

#define LT10 54

#define LT22 71
#define LT21 72
#define LT20 73

/**
 * Right Thumb
 */
#define RT00 37
#define RT01 38

#define RT10 57

#define RT20 74
#define RT21 75
#define RT22 76

/**
 * Groups
 */

#define LEFT_KEYS   L06 L05 L04 L03 L02 L01 L00 \
                    L16 L15 L14 L13 L12 L11 L10 \
                    L26 L25 L24 L23 L22 L21 L20 \
                    L35 L34 L33 L32 L31 L30 \
                    L44 L43 L42 L41 L40

#define RIGHT_KEYS  R00 R01 R02 R03 R04 R05 R06 \
                    R10 R11 R12 R13 R14 R15 R16 \
                    R20 R21 R22 R23 R24 R25 R26 \
                        R30 R31 R32 R33 R34 R35 \
                            R40 R41 R42 R43 R44 \

#define LEFT_THUMB_KEYS         LT01 LT00 \
                                     LT10 \
                           LT22 LT21 LT20

#define RIGHT_THUMB_KEYS    RT00 RT01      \
                            RT10           \
                            RT20 RT21 RT22

#define THUMB_KEYS LEFT_THUMB_KEYS RIGHT_THUMB_KEYS

#define LEFT_HAND_KEYS LEFT_KEYS LEFT_THUMB_KEYS

#define RIGHT_HAND_KEYS RIGHT_KEYS RIGHT_THUMB_KEYS

#define ALL_KEYS LEFT_KEYS LEFT_THUMB_KEYS RIGHT_THUMB_KEYS RIGHT_KEYS
