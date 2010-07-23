import re

void_elements = ['link', 'img', 'br', 'hr', 'extends', 'include', 'else', 'elif', 'except', 'finally']
template_keywords = ['extends', 'include', 'block', 'for', 'if', 'while', 'try']
intermediate_keywords = ['else', 'elif', 'except', 'finally']

def attr_if_any(name, value):
  if value:
    return '%s="%s"' % (name, value)
  else:
    return ""

def unwind_tag_stack(output, tag_stack, indent=""):
  while tag_stack and len(indent) <= len(tag_stack[-1].indent):
    old_li = tag_stack.pop()      
    output.append(old_li.close_pattern % (old_li.indent, old_li.tag))

class LineInfo(object):
  _whitespace_re = "(\s*)"
  _tag_re = "(?:%(\w*))?"
  _id_re = "(?:#((?:{{[^}]*}}|[-\w])+))?"
  _class_re = "((?:\.(?:[-\w]|{{.*}})+)*)"
  _attrs_re = "((?: [\w-]+=\"[^\"]*\")*)"
  _rest_re = "\s*(.*)"
  line_re = re.compile(''.join([_whitespace_re, _tag_re, _id_re, _class_re, _attrs_re, _rest_re]))
  close_pattern = "%s</%s>"
  open_pattern = "%s<%s>%s"

  def __init__(self, line):
    (self.indent, self.tag, self.id, self.classes, self.attrs, self.rest) = self.line_re.match(line).groups()
    if not self.tag and (self.id or self.classes):
      self.tag = 'div'
      
    if self.is_void_tag() and self.tag not in template_keywords \
          and self.tag not in intermediate_keywords:
      self.closing_slash = "/"
    else:
      self.closing_slash = ""

    if self.classes:
      self.classes = ' '.join(self.classes.split(".")[1:])
    if self.attrs:
      self.attrs = self.attrs[1:]
  
  def is_void_tag(self):
    return self.tag in void_elements
   
  def get_element_parts(self):
    return filter(None, 
        (self.tag, attr_if_any('id', self.id), attr_if_any('class', self.classes), 
        self.attrs, self.closing_slash))
 
class TornadoLineInfo(LineInfo):
  close_pattern = "%s{%% end %%} <!-- %s -->"
  open_pattern = "%s{%% %s %s %%}"

    
def convert_text(input):
  output = []
  tag_stack = []
  
  for line in input.split('\n'):
    if not line or line.isspace():
      continue

    li = LineInfo(line)

    if not li.tag and li.rest:
      unwind_tag_stack(output, tag_stack, li.indent)
      output.append(line)
      continue
    
    if li.tag in template_keywords:
      li = TornadoLineInfo(line)
    elif li.tag in intermediate_keywords:
      li = TornadoLineInfo(line)
      li.indent += ' ' # Stop unwinding at the parent statement

    unwind_tag_stack(output, tag_stack, li.indent)
    if not li.is_void_tag():
      tag_stack.append(li)
    
    output.append(li.open_pattern % (li.indent, ' '.join(li.get_element_parts()), li.rest))

  unwind_tag_stack(output, tag_stack)

  return '\n'.join(output)
  

