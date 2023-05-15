from __future__ import annotations
from typing import List, Dict, Tuple
from abc import ABC, abstractmethod
from enum import Enum

import os
import dominate
from dominate.tags import *
from dominate.util import raw

from domain.statistics_compute import StatisticValues                        
from domain.statistics_compute import ClassConnectionsDetails                        
from domain.diagram_creation import DiagramCreation

class StatisticsHtml:
    class PageCreator(ABC):
        class ColorizeTypeRisk(Enum):
            ANY = 1
            CHILD_CLASS = 2
            PARENT_CLASS = 3
            AGGREGATION_FROM = 4
            USES_FROM = 5
            AGGREGATION_TO = 6
            USES_TO = 7

        def __init__(self, title: str, statistics: StatisticValues, 
                    connection_details: Dict[str, ClassConnectionsDetails],
                    from_dir: str, colorize_type_risk: StatisticsHtml.PageCreator.ColorizeTypeRisk):
            self.doc: dominate.document = dominate.document(title=title)
            self.title = title
            self.statistics = statistics
            self.from_dir = from_dir
            self.colorize_type_risk = colorize_type_risk
            self.dict_connection_details = connection_details

        def _create_summary(self):
            with self.doc:
                h2("Main statistics")
            with self.doc:
                with div(id='statistics'):
                    table_links: table = table(border=1, 
                                            style="border-collapse: collapse; font-family: Monospace; " +
                                                    "box-shadow: 5px 10px 18px #888888; border: 3px solid purple; " +
                                                    "margin-left: auto; margin-right: auto; ")

                    self.doc.add(table_links)
                    with table_links:
                        default_color = '#000000'
                        with tr():
                            bgcolor: str = f'#888888'
                            td_style = f"padding-right: 5px; padding-left: 5px; "
                            with td(style=td_style, color = default_color, bgcolor = bgcolor, halign="center", valign="center"):
                                p("Statistic")
                            with td(style=td_style, color = default_color, bgcolor = bgcolor, halign="center", valign="center"):
                                p("Child classes")
                            with td(style=td_style, color = default_color, bgcolor = bgcolor, halign="center", valign="center"):
                                p("Parent classes")
                            with td(style=td_style, color = default_color, bgcolor = bgcolor, halign="center", valign="center"):
                                p("Aggregation from")
                            with td(style=td_style, color = default_color, bgcolor = bgcolor, halign="center", valign="center"):
                                p("Aggregation to")
                            with td(style=td_style, color = default_color, bgcolor = bgcolor, halign="center", valign="center"):
                                p("Uses from")
                            with td(style=td_style, color = default_color, bgcolor = bgcolor, halign="center", valign="center"):
                                p("Uses to")

                        with tr():
                            bgcolor: str = f'#888888'
                            td_style = f"padding-right: 5px; padding-left: 5px; "
                            with td(style=td_style, bgcolor = bgcolor, halign="center", valign="center"):
                                p("Thresholds")
                            bgcolor: str = f'#DDDDDD'
                            with td(style=td_style, color = default_color, bgcolor = bgcolor, halign="center", valign="center"):
                                p('{}'.format(ClassConnectionsDetails.THRESHOLD_CHILD_CLASSES))
                            with td(style=td_style, color = default_color, bgcolor = bgcolor, halign="center", valign="center"):
                                p('{}'.format(ClassConnectionsDetails.THRESHOLD_PARENT_CLASSES))
                            with td(style=td_style, color = default_color, bgcolor = bgcolor, halign="center", valign="center"):
                                p('{}'.format(ClassConnectionsDetails.THRESHOLD_AGGREGATION_FROM))
                            with td(style=td_style, color = default_color, bgcolor = bgcolor, halign="center", valign="center"):
                                p('{}'.format(ClassConnectionsDetails.THRESHOLD_AGGREGATION_TO))
                            with td(style=td_style, color = default_color, bgcolor = bgcolor, halign="center", valign="center"):
                                p('{}'.format(ClassConnectionsDetails.THRESHOLD_USES_FROM))
                            with td(style=td_style, color = default_color, bgcolor = bgcolor, halign="center", valign="center"):
                                p('{}'.format(ClassConnectionsDetails.THRESHOLD_USES_TO))

                        with tr():
                            bgcolor: str = f'#888888'
                            td_style = f"padding-right: 5px; padding-left: 5px; "
                            with td(style=td_style, color = default_color, bgcolor = bgcolor, halign="center", valign="center"):
                                p("Mean")
                            #bgcolor: str = f'#DDDDDD'
                            color = default_color
                            bgcolor = f'#DDDDDD' if self.statistics.mean.child_classes < ClassConnectionsDetails.THRESHOLD_CHILD_CLASSES else '#FF0000'
                            with td(style=td_style, color = color, bgcolor = bgcolor, halign="center", valign="center"):
                                p('{:.3f}'.format(self.statistics.mean.child_classes))

                            color = default_color
                            bgcolor: str = f'#DDDDDD'  if self.statistics.mean.parent_classes < ClassConnectionsDetails.THRESHOLD_PARENT_CLASSES else '#FF0000'
                            with td(style=td_style, color = color, bgcolor = bgcolor, halign="center", valign="center"):
                                p('{:.3f}'.format(self.statistics.mean.parent_classes))

                            color = default_color
                            bgcolor: str = f'#DDDDDD'  if self.statistics.mean.aggregations_from < ClassConnectionsDetails.THRESHOLD_AGGREGATION_FROM else '#FF0000'
                            with td(style=td_style, color = color, bgcolor = bgcolor, halign="center", valign="center"):
                                p('{:.3f}'.format(self.statistics.mean.aggregations_from))

                            color = default_color
                            bgcolor: str = f'#DDDDDD'  if self.statistics.mean.aggregations_to < ClassConnectionsDetails.THRESHOLD_AGGREGATION_TO else '#FF0000'
                            with td(style=td_style, color = color, bgcolor = bgcolor, halign="center", valign="center"):
                                p('{:.3f}'.format(self.statistics.mean.aggregations_to))

                            color = default_color
                            bgcolor: str = f'#DDDDDD'  if self.statistics.mean.uses_from < ClassConnectionsDetails.THRESHOLD_USES_FROM else '#FF0000'
                            with td(style=td_style, color = color, bgcolor = bgcolor, halign="center", valign="center"):
                                p('{:.3f}'.format(self.statistics.mean.uses_from))

                            color = default_color
                            bgcolor: str = f'#DDDDDD'  if self.statistics.mean.uses_to < ClassConnectionsDetails.THRESHOLD_USES_TO else '#FF0000'
                            with td(style=td_style, color = color, bgcolor = bgcolor, halign="center", valign="center"):
                                p('{:.3f}'.format(self.statistics.mean.uses_to))

                        with tr():
                            bgcolor: str = f'#888888'
                            td_style = f"padding-right: 5px; padding-left: 5px; "
                            with td(style=td_style, bgcolor = bgcolor, halign="center", valign="center"):
                                p("Variance")
                            bgcolor: str = f'#DDDDDD'
                            with td(style=td_style, color = default_color, bgcolor = bgcolor, halign="center", valign="center"):
                                p('{:.3f}'.format(self.statistics.variance.child_classes))
                            with td(style=td_style, color = default_color, bgcolor = bgcolor, halign="center", valign="center"):
                                p('{:.3f}'.format(self.statistics.variance.parent_classes))
                            with td(style=td_style, color = default_color, bgcolor = bgcolor, halign="center", valign="center"):
                                p('{:.3f}'.format(self.statistics.variance.aggregations_from))
                            with td(style=td_style, color = default_color, bgcolor = bgcolor, halign="center", valign="center"):
                                p('{:.3f}'.format(self.statistics.variance.aggregations_to))
                            with td(style=td_style, color = default_color, bgcolor = bgcolor, halign="center", valign="center"):
                                p('{:.3f}'.format(self.statistics.variance.uses_from))
                            with td(style=td_style, color = default_color, bgcolor = bgcolor, halign="center", valign="center"):
                                p('{:.3f}'.format(self.statistics.variance.uses_to))

                        with tr():
                            bgcolor: str = f'#888888'
                            td_style = f"padding-right: 5px; padding-left: 5px; "
                            with td(style=td_style, color = default_color, bgcolor = bgcolor, halign="center", valign="center"):
                                p("Max")
                            
                            color = default_color
                            bgcolor: str = f'#DDDDDD' if self.statistics.max.child_classes < ClassConnectionsDetails.THRESHOLD_CHILD_CLASSES else '#FF0000'
                            with td(style=td_style, color = color, bgcolor = bgcolor, halign="center", valign="center"):
                                p('{}'.format(self.statistics.max.child_classes))

                            color = default_color 
                            bgcolor: str = f'#DDDDDD' if self.statistics.max.parent_classes < ClassConnectionsDetails.THRESHOLD_PARENT_CLASSES else '#FF0000'
                            with td(style=td_style, color = color, bgcolor = bgcolor, halign="center", valign="center"):
                                p('{}'.format(self.statistics.max.parent_classes))

                            color = default_color 
                            bgcolor: str = f'#DDDDDD' if self.statistics.max.aggregations_from < ClassConnectionsDetails.THRESHOLD_AGGREGATION_FROM else '#FF0000'
                            with td(style=td_style, color = color, bgcolor = bgcolor, halign="center", valign="center"):
                                p('{}'.format(self.statistics.max.aggregations_from))

                            color = default_color 
                            bgcolor: str = f'#DDDDDD' if self.statistics.max.aggregations_to < ClassConnectionsDetails.THRESHOLD_AGGREGATION_TO else '#FF0000'
                            with td(style=td_style, color = color, bgcolor = bgcolor, halign="center", valign="center"):
                                p('{}'.format(self.statistics.max.aggregations_to))

                            color = default_color 
                            bgcolor: str = f'#DDDDDD' if self.statistics.max.uses_from < ClassConnectionsDetails.THRESHOLD_USES_FROM else '#FF0000'
                            with td(style=td_style, color = color, bgcolor = bgcolor, halign="center", valign="center"):
                                p('{}'.format(self.statistics.max.uses_from))

                            color = default_color 
                            bgcolor: str = f'#DDDDDD' if self.statistics.max.uses_to < ClassConnectionsDetails.THRESHOLD_USES_TO else '#FF0000'
                            with td(style=td_style, color = color, bgcolor = bgcolor, halign="center", valign="center"):
                                p('{}'.format(self.statistics.max.uses_to))


 
        @staticmethod
        def _status_number_connections(connection_type: str,
                                    number: int, max_number: int, threshold: int) -> Tuple[str, float]:
            return_string: str = ''
            risk: float = 0.0
            if max_number > threshold and number > threshold:
                return_string = f' <b>{connection_type}</b>'
                if number < max_number / 100:
                    return_string += f' ({number} < 1% max)'
                    risk = 0.1
                elif number < max_number / 10:
                    return_string += f' ({number} = {number * 100 // max_number}% max)'
                    risk = 0.3
                elif number < max_number / 2:
                    return_string += f' ({number} = {number * 100 // max_number}% max)'
                    risk = 0.5
                elif number < 2 * max_number / 3:
                    return_string += f' ({number} = {number * 100 // max_number}% max)'
                    risk = 0.8
                else:
                    return_string += f' ({number} = {number * 100 // max_number}% max)'
                    risk = 1.0
            return return_string, risk

        def _create_text(self, connection_details: ClassConnectionsDetails, target_directory) -> str:

            dict_status_string_risk: Dict[StatisticsHtml.PageCreator.ColorizeTypeRisk, Tuple[str, float]] = {}

            dict_status_string_risk[StatisticsHtml.PageCreator.ColorizeTypeRisk.AGGREGATION_FROM] = \
                StatisticsHtml.PageCreator._status_number_connections(
                    'aggrg from',
                    connection_details.get_number_aggregations_from(), self.statistics.max.aggregations_from,
                    ClassConnectionsDetails.THRESHOLD_AGGREGATION_FROM)
            dict_status_string_risk[StatisticsHtml.PageCreator.ColorizeTypeRisk.CHILD_CLASS] = \
                StatisticsHtml.PageCreator._status_number_connections(
                    'child classes',
                    connection_details.get_number_child_classes(), self.statistics.max.child_classes,
                    ClassConnectionsDetails.THRESHOLD_CHILD_CLASSES)
            dict_status_string_risk[StatisticsHtml.PageCreator.ColorizeTypeRisk.USES_FROM] = \
                StatisticsHtml.PageCreator._status_number_connections(
                    'uses from',
                    connection_details.get_number_uses_from(), self.statistics.max.uses_from,
                    ClassConnectionsDetails.THRESHOLD_USES_FROM)
            dict_status_string_risk[StatisticsHtml.PageCreator.ColorizeTypeRisk.AGGREGATION_TO] = \
                StatisticsHtml.PageCreator._status_number_connections(
                    'aggrg to',
                    connection_details.get_number_aggregations_to(), self.statistics.max.aggregations_to,
                    ClassConnectionsDetails.THRESHOLD_AGGREGATION_TO)
            dict_status_string_risk[StatisticsHtml.PageCreator.ColorizeTypeRisk.PARENT_CLASS] = \
                StatisticsHtml.PageCreator._status_number_connections(
                    'parent classes',
                    connection_details.get_number_parent_classes(), self.statistics.max.parent_classes,
                    ClassConnectionsDetails.THRESHOLD_PARENT_CLASSES)
            dict_status_string_risk[StatisticsHtml.PageCreator.ColorizeTypeRisk.USES_TO] = \
                StatisticsHtml.PageCreator._status_number_connections(
                    'uses to',
                    connection_details.get_number_uses_to(), self.statistics.max.uses_to,
                    ClassConnectionsDetails.THRESHOLD_USES_TO)
            
            links_string: str = ''
            class_name: str = connection_details.get_class_name()
            main_link = ""
            for grouped_per_ns in [True, False]:
                for detailed in [True, False]:
                    svg_file = DiagramCreation.get_file_name_from_class_namespace_name(detailed, grouped_per_ns, class_name, want_svg_file=True)
                    user_info: str = ('detailed' if detailed else 'concise')
                    user_info += ' AND <b>grouped per NS</b>' if grouped_per_ns else ''
                    link_class = 'table_link'
                    broken_link = '' 
                    if not os.path.isfile(os.path.join(target_directory, svg_file)):
                        link_class = 'broken_link'
                        broken_link = '&#9888;broken&#9888;'
                    links_string += f' <a class="{link_class}" href="{svg_file}">{user_info}</a> {broken_link}<br>'
                    if len(main_link) == 0:
                        main_link = f'<a class="{link_class}" href="{svg_file}">{class_name}</a> {broken_link}'
            status_string: str = "<br>".join([status_string for status_string, _ in dict_status_string_risk.values() 
                                            if isinstance(status_string, str) and len(status_string.strip()) > 0])
            status_risk: Dict[StatisticsHtml.PageCreator.ColorizeTypeRisk, float] = \
                {status_risk_key: status_string_risk[1] for status_risk_key, status_string_risk in dict_status_string_risk.items()}

            return status_string, status_risk, links_string, main_link

        def _create_page(self, target_directory: str) -> str:
            
            with self.doc.head:
                style("""\

                    a.table_link:link     { color: white; }
                    a.table_link:visited  { color: purple; }
                    a.table_link:hover    { color: black; }
                    a.table_link:active   { color: blue; }

                    a.normal:link     { color: blue; }
                    a.normal:visited  { color: darkblue; }
                    a.normal:hover    { color: black; }
                    a.normal:active   { color: green; }

                    a.broken_link:link     { color: black; }
                    a.broken_link:visited  { color: darkblue; }
                    a.broken_link:hover    { color: hotpink; }
                    a.broken_link:active   { color: blue; }
                """)

            with self.doc:
                with div(id='detailed_results'):
                    table_links: table = table(border=1, 
                                            style="border-collapse: collapse; font-family: Monospace; " +
                                                    "box-shadow: 5px 10px 18px #888888; border: 3px solid purple; " +
                                                    "margin-left: auto; margin-right: auto; ")

                    
                    self.doc.add(table_links)
                    with table_links:
                        for class_name in self.get_connection_details_keys():
                            status_string, status_risk, links_string, main_link = \
                                self._create_text(self.dict_connection_details[class_name], target_directory)
                            with tr():
                                risk = max(status_risk.values()) if self.colorize_type_risk == StatisticsHtml.PageCreator.ColorizeTypeRisk.ANY \
                                                                else status_risk[self.colorize_type_risk]
                                red: str = hex(int(255 * risk))[2:] #if risk >= 0.3 else '00'
                                green: str = hex(int(255 * (1 - risk)))[2:] #if risk < 0.3 else '00'
                                bgcolor: str = f'#{red}{green}00'
                                td_style = f"padding-right: 5px; padding-left: 5px; font-size: 15 px; color: #FFFFFF"
                                with td(style=td_style, color = '#FFFFFF', bgcolor = bgcolor, halign="left", valign="center"):
                                    with p():
                                        p(raw(main_link))
                                    
                                with td(style=td_style, bgcolor = bgcolor, halign="center", valign="center"):
                                    with p():
                                        p(raw(links_string))

                                with td(style=td_style, bgcolor = bgcolor, halign="center", valign="center"):
                                    with p():
                                        p(raw(status_string))


        def _create_header(self) -> None:
            with self.doc:
                h1(raw(f"<center>RevEngEr</center>"))
                h1(raw(f"Results for {self.from_dir}"))
            with self.doc:
                self._create_summary()


        def _create_links(self, file_name: str, link_file_names: List[Tuple[str, str]]) -> None:
            if len(link_file_names) > 0:
                with self.doc:
                    for link_file_description, link_file_name in link_file_names:
                        if link_file_name != file_name:
                            with p():
                                p(raw(f'<a class="normal" href="{os.path.basename(link_file_name)}">{link_file_description}</a>'))

        def create_page(self, file_name: str, link_file_names: List[Tuple[str, str]],
                        target_directory: str):
            self.doc.add(h1(raw(self.title)))

            self._create_header()
            self._create_links(file_name, link_file_names)
            self._create_page(target_directory)
        
            with open(file_name, 'w') as f:
                f.write(self.doc.render())
        
        @abstractmethod
        def get_connection_details_keys(self):
            pass
    
    class PageCreatorClassNamesSortedPerAnyRisk(PageCreator):
        def __init__(self, statistics: StatisticValues, 
                    connection_details: Dict[str, ClassConnectionsDetails],
                    from_dir: str):
            super().__init__("List of classes ordered by <b>any risk</b>", statistics,
                             connection_details, from_dir, 
                             StatisticsHtml.PageCreator.ColorizeTypeRisk.ANY)
        def get_connection_details_keys(self):
            return [k for k, _ in 
                    sorted(self.dict_connection_details.items(), 
                            key=lambda item: item[1].get_max_of_all(), reverse=True)]
        
    class PageCreatorClassNamesSortedPerName(PageCreator):
        def __init__(self, statistics: StatisticValues, 
                    connection_details: Dict[str, ClassConnectionsDetails],
                    from_dir: str):
            super().__init__("List of classes <b>ordered alphabetically</b>", statistics,
                             connection_details, from_dir, 
                             StatisticsHtml.PageCreator.ColorizeTypeRisk.ANY)
        def get_connection_details_keys(self):
            return sorted(self.dict_connection_details.keys())

    class PageCreatorClassNamesSortedPerChildClassesRisk(PageCreator):
        def __init__(self, statistics: StatisticValues, 
                    connection_details: Dict[str, ClassConnectionsDetails],
                    from_dir: str):
            super().__init__("List of classes ordered per <b>child class</b> risk", statistics,
                             connection_details, from_dir, 
                             StatisticsHtml.PageCreator.ColorizeTypeRisk.CHILD_CLASS)

        def get_connection_details_keys(self):
            return [k for k, _ in 
                    sorted(self.dict_connection_details.items(), 
                            key=lambda item: item[1].get_number_child_classes(), reverse=True)]
        
    class PageCreatorClassNamesSortedPerParentClassesRisk(PageCreator):
        def __init__(self, statistics: StatisticValues, 
                    connection_details: Dict[str, ClassConnectionsDetails],
                    from_dir: str):
            super().__init__("List of classes ordered per <b>parent class</b> risk", statistics,
                             connection_details, from_dir, 
                             StatisticsHtml.PageCreator.ColorizeTypeRisk.PARENT_CLASS)

        def get_connection_details_keys(self):
            return [k for k, _ in 
                    sorted(self.dict_connection_details.items(), 
                            key=lambda item: item[1].get_number_parent_classes(), reverse=True)]            

    class PageCreatorClassNamesSortedPerAggregationFrom(PageCreator):
        def __init__(self, statistics: StatisticValues, 
                    connection_details: Dict[str, ClassConnectionsDetails],
                    from_dir: str):
            super().__init__("List of classes ordered per <b>aggregation from</b> risk", statistics,
                             connection_details, from_dir, 
                             StatisticsHtml.PageCreator.ColorizeTypeRisk.AGGREGATION_FROM)

        def get_connection_details_keys(self):
            return [k for k, _ in 
                    sorted(self.dict_connection_details.items(), 
                            key=lambda item: item[1].get_number_aggregations_from(), reverse=True)]              

    class PageCreatorClassNamesSortedPerAggregationTo(PageCreator):
        def __init__(self, statistics: StatisticValues, 
                    connection_details: Dict[str, ClassConnectionsDetails],
                    from_dir: str):
            super().__init__("List of classes ordered per <b>aggregation to</b> risk", statistics,
                             connection_details, from_dir, 
                             StatisticsHtml.PageCreator.ColorizeTypeRisk.AGGREGATION_TO)

        def get_connection_details_keys(self):
            return [k for k, _ in 
                    sorted(self.dict_connection_details.items(), 
                            key=lambda item: item[1].get_number_aggregations_to(), reverse=True)]              

    class PageCreatorClassNamesSortedPerUsesFrom(PageCreator):
        def __init__(self, statistics: StatisticValues, 
                    connection_details: Dict[str, ClassConnectionsDetails],
                    from_dir: str):
            super().__init__("List of classes ordered per <b>uses from</b> risk", statistics,
                             connection_details, from_dir, 
                             StatisticsHtml.PageCreator.ColorizeTypeRisk.USES_FROM)

        def get_connection_details_keys(self):
            return [k for k, _ in 
                    sorted(self.dict_connection_details.items(), 
                            key=lambda item: item[1].get_number_uses_from(), reverse=True)]            

    class PageCreatorClassNamesSortedPerUsesTo(PageCreator):
        def __init__(self, statistics: StatisticValues, 
                    connection_details: Dict[str, ClassConnectionsDetails],
                    from_dir: str):
            super().__init__("List of classes ordered per <b>uses from</b> risk", statistics,
                             connection_details, from_dir, 
                             StatisticsHtml.PageCreator.ColorizeTypeRisk.USES_TO)

        def get_connection_details_keys(self):
            return [k for k, _ in 
                    sorted(self.dict_connection_details.items(), 
                            key=lambda item: item[1].get_number_uses_to(), reverse=True)]                

    def create(connection_details: Dict[str, ClassConnectionsDetails],
               statistics: StatisticValues,
               from_dir: str, out_dir: str):
        
        target_directory: str = os.path.join(os.getcwd(), out_dir)
        main_filename: str                  = os.path.join(target_directory, 'index.html')
        index_alphabetially_ordered: str    = os.path.join(target_directory, 'index_alphabetially_ordered.html')
        index_child_classes_ordered: str    = os.path.join(target_directory, 'index_child_classes_ordered.html')
        index_parent_classes_ordered: str   = os.path.join(target_directory, 'index_parent_classes_ordered.html')
        index_aggregation_from_ordered: str = os.path.join(target_directory, 'index_aggregation_from_ordered.html')
        index_aggregation_to_ordered: str   = os.path.join(target_directory, 'index_aggregation_to_ordered.html')
        index_uses_to_ordered: str          = os.path.join(target_directory, 'index_uses_to_ordered.html')
        index_uses_from_ordered: str        = os.path.join(target_directory, 'index_uses_from_ordered.html')

        link_file_names: List[Tuple[str, str]] = [
            ('Home', main_filename),
            ('Classes ordered alphabetically', index_alphabetially_ordered),
            ('Classes ordered by child classes risk', index_child_classes_ordered),
            ('Classes ordered by parent classes risk', index_parent_classes_ordered),
            ('Classes ordered by aggregation from risk', index_aggregation_from_ordered),
            ('Classes ordered by aggregation to risk', index_aggregation_to_ordered),
            ('Classes ordered by uses to risk', index_uses_to_ordered),
            ('Classes ordered by uses from risk', index_uses_from_ordered)
        ]

        StatisticsHtml.PageCreatorClassNamesSortedPerAnyRisk(
            statistics, 
            connection_details,
            from_dir).create_page(main_filename, link_file_names, target_directory)

        StatisticsHtml.PageCreatorClassNamesSortedPerName(
            statistics, 
            connection_details,
            from_dir).create_page(index_alphabetially_ordered, link_file_names, target_directory)

        StatisticsHtml.PageCreatorClassNamesSortedPerChildClassesRisk(
            statistics, 
            connection_details,
            from_dir).create_page(index_child_classes_ordered, link_file_names, target_directory)

        StatisticsHtml.PageCreatorClassNamesSortedPerParentClassesRisk(
            statistics, 
            connection_details,
            from_dir).create_page(index_parent_classes_ordered, link_file_names, target_directory)

        StatisticsHtml.PageCreatorClassNamesSortedPerAggregationFrom(
            statistics, 
            connection_details,
            from_dir).create_page(index_aggregation_from_ordered, link_file_names, target_directory)

        StatisticsHtml.PageCreatorClassNamesSortedPerAggregationTo(
            statistics, 
            connection_details,
            from_dir).create_page(index_aggregation_to_ordered, link_file_names, target_directory)

        StatisticsHtml.PageCreatorClassNamesSortedPerUsesFrom(
            statistics, 
            connection_details,
            from_dir).create_page(index_uses_from_ordered, link_file_names, target_directory)

        StatisticsHtml.PageCreatorClassNamesSortedPerUsesTo(
            statistics, 
            connection_details,
            from_dir).create_page(index_uses_to_ordered, link_file_names, target_directory)

        return main_filename

