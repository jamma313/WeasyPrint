# coding: utf8

#  WeasyPrint converts web documents (HTML, CSS, ...) to PDF.
#  Copyright (C) 2011  Simon Sapin
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
    Expand shorthand properties.
    eg. margin becomes margin-top, margin-right, margin-bottom and margin-left.
"""


import functools

from cssutils.css import PropertyValue

from .values import get_keyword, get_single_keyword


# See http://www.w3.org/TR/CSS21/propidx.html
INITIAL_VALUES = dict(
    (name, list(PropertyValue(value)))
    for name, value in [
        ('background-attachment', 'scroll'),
        ('background-color', 'transparent'),
        ('background-image', 'none'),
        ('background-position', '0% 0%'),
        ('background-repeat', 'repeat'),
        ('border-collapse', 'separate'),
        # http://www.w3.org/TR/css3-color/#currentcolor
        ('border-top-color', 'currentColor'),
        ('border-right-color', 'currentColor'),
        ('border-bottom-color', 'currentColor'),
        ('border-left-color', 'currentColor'),
        ('border-spacing', '0'),
        ('border-top-style', 'none'),
        ('border-right-style', 'none'),
        ('border-bottom-style', 'none'),
        ('border-left-style', 'none'),
        ('border-top-width', 'medium'),
        ('border-right-width', 'medium'),
        ('border-bottom-width', 'medium'),
        ('border-left-width', 'medium'),
        ('bottom', 'auto'),
        ('caption-side', 'top'),
        ('clear', 'none'),
        ('clip', 'auto'),
        ('color', '#000'),     # depends on user agent
        ('content', 'normal'),
        ('counter-increment', 'none'),
        ('counter-reset', 'none'),
        ('direction', 'ltr'),
        ('display', 'inline'),
        ('empty-cells', 'show'),
        ('float', 'none'),
        ('font-family', 'serif'), # depends on user agent
        ('font-size', 'medium'),
        ('font-style', 'normal'),
        ('font-variant', 'normal'),
        ('font-weight', 'normal'),
        ('height', 'auto'),
        ('left', 'auto'),
        ('letter-spacing', 'normal'),
        ('line-height', 'normal'),
        ('list-style-image', 'none'),
        ('list-style-position', 'outside'),
        ('list-style-type', 'disc'),
        ('margin-top', '0'),
        ('margin-right', '0'),
        ('margin-bottom', '0'),
        ('margin-left', '0'),
        ('max-height', 'none'),
        ('max-width', 'none'),
        ('min-height', '0'),
        ('min-width', '0'),
        ('orphans', '2'),
        ('overflow', 'visible'),
        ('padding-top', '0'),
        ('padding-right', '0'),
        ('padding-bottom', '0'),
        ('padding-left', '0'),
        ('page-break-after', 'auto'),
        ('page-break-before', 'auto'),
        ('page-break-inside', 'auto'),
        ('quotes', u'"“" "”" "‘" "’"'),  # depends on user agent
        ('position', 'static'),
        ('right', 'auto'),
        ('table-layout', 'auto'),
        ('text-align', 'start'),  # Taken from CSS3 Text
                                 # Other CSS3 values are not supported.
        ('text-decoration', 'none'),
        ('text-indent', '0'),
        ('text-transform', 'none'),
        ('top', 'auto'),
        ('unicode-bidi', 'normal'),
        ('vertical-align', 'baseline'),
        ('visibility', 'visible'),
        ('white-space', 'normal'),
        ('widows', '2'),
        ('width', 'auto'),
        ('word-spacing', 'normal'),
        ('z-index', 'auto'),

        # CSS3 Paged Media: http://www.w3.org/TR/css3-page/#page-size
        ('size', 'auto'),
    ]
)


# Not applicable to the print media
NOT_PRINT_MEDIA = set([
    # Aural media:
    'azimuth',
    'cue',
    'cue-after',
    'cue-before',
    'cursor',
    'elevation',
    'pause',
    'pause-after',
    'pause-before',
    'pitch-range',
    'pitch',
    'play-during',
    'richness',
    'speak-header',
    'speak-numeral',
    'speak-punctuation',
    'speak',
    'speech-rate',
    'stress',
    'voice-family',
    'volume',

    # Outlines only apply to interactive media, just like cursor.
    'outline'
    'outline-color',
    'outline-style',
    'outline-width',
])


# Do not list shorthand properties here as we handle them before inheritance.
#
# text-decoration is not a really inherited, see
# http://www.w3.org/TR/CSS2/text.html#propdef-text-decoration
INHERITED = set("""
    border-collapse
    border-spacing
    caption-side
    color
    direction
    empty-cells
    font-family
    font-size
    font-style
    font-variant
    font-weight
    letter-spacing
    line-height
    list-style-image
    list-style-position
    list-style-type
    orphans
    quotes
    text-align
    text-decoration
    text-indent
    text-transform
    visibility
    white-space
    widows
    word-spacing
""".split())

# Inherited but not applicable to print:
#    azimuth
#    cursor
#    elevation
#    pitch-range
#    pitch
#    richness
#    speak-header
#    speak-numeral
#    speak-punctuation
#    speak
#    speech-rate
#    stress
#    voice-family
#    volume