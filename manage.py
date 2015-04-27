#!/usr/bin/env python


def validate_structural_line(substring):
    if len(substring) == 0:
        return True
    for character in substring:
        if character != " " and character != "\t":
            return False
    return True


def is_structural(line):
    bullet_position = line.find('*')
    bullet_found = bullet_position >= 0
    if not bullet_found:
        return False
    line_before_bullet = line[:bullet_position]
    is_valid_line = validate_structural_line(line_before_bullet)
    return is_valid_line


def parse_path(path):
    chapter_context = path.find("chapters") >= 0
    if chapter_context:
        chapter_id_start = path.find("chapter_") + len("chapter_")
        chapter_id_start_found = chapter_id_start >= 0
        if chapter_id_start_found:
            chapter_id_end = chapter_id_start + path[chapter_id_start:].find("/")
            chapter_id = int(path[chapter_id_start:chapter_id_end])
            section_path = path[chapter_id_end + 1:]
            section_id_start = section_path.find("section_") + len("section_")
            section_id_start_found = section_id_start >= 0
            if section_id_start_found:
                section_id_end = section_id_start + section_path[section_id_start:].find(".md")
                section_id = section_path[section_id_start:section_id_end]
                if section_id == "":
                    section_id = "-1"
                section_id = int(section_id)
                return [chapter_id, section_id]
            else:
                return [chapter_id, -1]
        else:
            return [-1, -1]


def parse_line(line):
    title_start = line.find("[") + 1
    title_end = line.find("]")
    path_start = line.find("(") + 1
    path_end = line.find(")")
    title = line[title_start:title_end]
    path = line[path_start:path_end]
    structure_vector = parse_path(path)
    return {"chapter_id": structure_vector[0],
            "section_id": structure_vector[1],
            "title": title,
            "path": path
           }


class ContentMatrix:

    def new_chapter(self, chapter_id, chapter_title, path):
        self.__matrix[chapter_id] = {'id': chapter_id, 'title': chapter_title, 'path': path, 'sections': []}

    def new_section(self, chapter_id, section_id, section_title, path):
        new_section_entry = {'id': section_id, 'title': section_title, 'path': path}
        self.__matrix[chapter_id]['sections'].append(new_section_entry)

    def print_matrix(self):

        section_number = 0

        for chapter in self.__matrix:
            chapter_record = self.__matrix[chapter]
            chapter_id = chapter_record['id']
            chapter_title = chapter_record['title']
            chapter_path = chapter_record['path']

            print "* CHAPTER %d | Title: %s | Path: %s" % (chapter_id, chapter_title, chapter_path)


            for section in chapter_record['sections']:
                section_id = section['id']
                section_title = section['title']
                section_path = section['path']
                print "\t- SECTION %d | Title: %s | Path: %s" % (section_id, section_title, section_path)

            section_number += len(chapter_record['sections'])
            print "/* SUM: %d sections in this chapter. */\n" % len(chapter_record['sections'])

        print "/* SUM: %d chapters and %d sections have been written.*/\n" % (len(self.__matrix), section_number)

    __matrix = {}


def main():
    content_matrix = ContentMatrix()
    summary_file = open("SUMMARY.md", "r")
    summary_content = summary_file.read()
    summary_parsed_content = summary_content.splitlines()
    for line in summary_parsed_content:
        if is_structural(line):
            parsed_line = parse_line(line)
            if parsed_line['section_id'] > 0:
                content_matrix.new_section(parsed_line['chapter_id'], parsed_line['section_id'], parsed_line['title'], parsed_line['path'])
            else:
                content_matrix.new_chapter(parsed_line['chapter_id'], parsed_line['title'], parsed_line['path'])

    content_matrix.print_matrix()
    return 0


if __name__ == "__main__":
    main()
