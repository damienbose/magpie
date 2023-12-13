from .xml_edits import NodeDeletion, NodeReplacement, NodeInsertion, NodeMoving, NodeSwap
from .xml_edits import TextSetting, TextWrapping

class XmlLineDeletion(NodeDeletion):
    NODE_TYPE = 'line'

class XmlLineReplacement(NodeReplacement):
    NODE_TYPE = 'line'

class XmlLineInsertion(NodeInsertion):
    NODE_PARENT_TYPE = 'unit'
    NODE_TYPE = 'line'

class XmlLineMoving(NodeMoving):
    NODE_PARENT_TYPE = 'unit'
    NODE_TYPE = 'line'

class StmtDeletion(NodeDeletion):
    NODE_TYPE = 'stmt'

# break continue decl_stmt do expr_stmt for goto if return switch while
class BreakDeletion(NodeDeletion):
    NODE_TYPE = 'break'

class ContinueDeletion(NodeDeletion):
    NODE_TYPE = 'continue'

class DeclStmtDeletion(NodeDeletion):
    NODE_TYPE = 'decl_stmt'

class DoDeletion(NodeDeletion):
    NODE_TYPE = 'do'

class ExprStmtDeletion(NodeDeletion):
    NODE_TYPE = 'expr_stmt'

class ForDeletion(NodeDeletion):
    NODE_TYPE = 'for'

class GotoDeletion(NodeDeletion):
    NODE_TYPE = 'goto'

class IfDeletion(NodeDeletion):
    NODE_TYPE = 'if'

class ReturnDeletion(NodeDeletion):
    NODE_TYPE = 'return'

class SwitchDeletion(NodeDeletion):
    NODE_TYPE = 'switch'

class WhileDeletion(NodeDeletion):
    NODE_TYPE = 'while'

class StmtReplacement(NodeReplacement):
    NODE_TYPE = 'stmt'

class StmtInsertion(NodeInsertion):
    NODE_PARENT_TYPE = 'block'
    NODE_TYPE = 'stmt'

class StmtMoving(NodeMoving):
    NODE_PARENT_TYPE = 'block'
    NODE_TYPE = 'stmt'

class StmtSwap(NodeSwap):
    NODE_PARENT_TYPE = 'block'
    NODE_TYPE = 'stmt'

class ConditionReplacement(NodeReplacement):
    NODE_TYPE = 'condition'

class ExprReplacement(NodeReplacement):
    NODE_TYPE = 'expr'

class ComparisonOperatorSetting(TextSetting):
    NODE_TYPE = 'operator_comp'
    CHOICES = ['==', '!=', '<', '<=', '>', '>=']

class ArithmeticOperatorSetting(TextSetting):
    NODE_TYPE = 'operator_arith'
    CHOICES = ['+', '-', '*', '/', '%']

class NumericSetting(TextSetting):
    NODE_TYPE = 'number'
    CHOICES = ['-1', '0', '1']

class RelativeNumericSetting(TextWrapping):
    NODE_TYPE = 'number'
    CHOICES = [('(', '+1)'), ('(', '-1)'), ('(', '/2)'), ('(', '*2)'), ('(', '*3/2)'), ('(', '*2/3)')]
