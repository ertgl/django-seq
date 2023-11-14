### [django-seq](#)

Django implementation of gapless sequences, with a configurable field type.

---


### Why?

Some departments require their data to have IDs in sequential order. For
example in a financial system, the invoice IDs would likely need to be in
sequential order.

In database management systems, sequences are used to generate unique
identifiers (IDs) for rows. For DBMs to support concurrency, it is possible
generated IDs to be discarded. Which leads to have gaps between the IDs.

Widely used DBMs such as PostgreSQL support concurrent operations. In order
to support concurrent operations; sequence changes made during insert
operations are never undone if an operation fails. Let's think we have
two concurrent transactions. The first inserts a row with ID `1` and the
second inserts a row with ID `2`. If the first fails, ID `1` will be
discarded. Because insertion the row has been cancelled. Also, the second
transaction **does not** reduce the ID of the second row. As a result, the
ID of the first row in the table will be `2` instead of `1`. We can consider
the same scenario with different IDs. So, the discarded IDs are the gaps
between the existing IDs. This is due to the nature of conflict/lock-free
algorithms used in
[OLTP](https://en.wikipedia.org/wiki/Online_transaction_processing)
environments.


### How?

One way to solve this problem is to take control of sequence generation
through a table and make the process part of the `transaction` to be
executed. Thus, if the transaction fails, the change on the sequences
table can be rolled back automatically. `django-seq` follows this approach.


**Table:** sequences

| **key** | **value** |
| ------- | --------- |
| ...     | ...       |


While inserting a data, make sure that the operation is within a
transaction. In the same transaction, select the corresponding
sequence row by locking it for update. If it exists, update the
sequence row with the next value. Otherwise, insert a sequence row
with value `1`. At the end of both cases, set data's ID to the value
of the sequence.


### Installation

`django-seq` is available on [PyPI](https://pypi.org/project/django-seq/).
It can be installed and upgraded using [pip](https://pip.pypa.io):

```shell
pip install django-seq
```


### Usage

`django-seq` provides both high and low level APIs to manage sequences.
While the high level one increases the development speed, the low level one
gives developers more control over the sequence generation and allows it to
be used for different situations than the simple CRUD.

Most of the time, using the high level API will suffice. Moreover, it
requires almost no change in the logic of any application.
See the section [SequenceField](#SequenceField) for more information.


### SequenceField

`SequenceField` is a subclass of `PositiveBigIntegerField` that can be used
to automatically generate unique IDs for model instances.

When a `SequenceField` is added to a model, `pre_save` signal is connected
for that model. When the signal is fired, the sequence is updated with the
next value. By default, the sequence name is the name of the model's table.
You are free to customize the sequence name by specifying the `key`
parameter. You can specify the key with the following types:

- `int`: The value will be converted to string.
- `str`: The string will be used as is.
- `django.db.models.F`: The value should be a pointer to a field of the
    model instance or one of its relations. Allowed relationship types are
    `one to one` and `many to one`. If the value points to a model instance,
    it will be replaced with the primary key of the instance.
- `list`: Objects in the list can be any of the above types. The evaluated
    list members will be joined with the `separator` parameter's value
    (which defaults to `.`) to form the sequence name.
- `tuple`: Same as `list`.
- `callable`: The callable will be called with the model instance being
    saved, as the only argument. The return value will be used in the
    sequence generation process. The callable can return any of the above
    types.

**Note:** If the evaluated key is a falsy value
(an empty string or `None` in this context), the sequence generation process
will be skipped for that model instance.


#### Generating IDs using SequenceField

Add the field to your model like any other field:

```python
from django.db import models
from django_seq.models import SequenceField


class Invoice(models.Model):

    number = SequenceField()
```


#### Generating IDs based on dependant fields

One of possible use cases of `django-seq` is to generate IDs based on some
dependant fields. For example, in an issue tracking system, it may be
preferable to generate issues' IDs based on the projects they belong to.
This can be achieved by specifying the `key` parameter as a list like below:

```python
from django.db import models
from django_seq.models import SequenceField


class Project(models.Model):
    pass


class Issue(models.Model):

    project = models.ForeignKey(
        to=Project,
        on_delete=models.CASCADE,
    )

    index = SequenceField(
        key=['projects', models.F('project'), 'issues'],
    )

    class Meta:

        unique_together = (('project', 'index'),)
```

The sequence name will be in the format of `projects.<project_id>.issues`
where `<project_id>` is the primary key of the project. Thus, each project
will have its own sequence for its issues, that starts from `1`.


#### Enabling automatic gap filling

To make the sequence generator fill the gaps, set `fill_gaps` parameter as `True`
or a callable that takes model instance as a parameter and returns `True`. This is
useful when you want the deleted IDs to be reused. So, the sequence generator will
generate an ID based on the first gap it finds, then sets the current value of the
sequence to that new ID.

```python
from django.db import models
from django_seq.models import SequenceField


class Item(models.Model):

    number = SequenceField(
      fill_gaps=True,
    )
```


#### Enabling automatic integrity error resolution

In some cases, the sequence generator may fail to generate a unique ID. For example,
when the sequence is used in a unique constraint and the current value is updated
manually in a way that causes the generator to generate an ID that already exists.
In such cases, the operation raises `IntegrityError`.

To make the sequence generator resolve the integrity errors automatically, set
`resolve_integrity_errors` parameter as `True` or a callable that takes model instance
as a parameter and returns `True`. So, the sequence generator will generate an ID based
on the first gap it finds after the last generated ID, then sets the current value of the
sequence to that new ID.

```python
from django.db import models
from django_seq.models import SequenceField


def _should_resolve_integrity_errors(invoice: "Invoice") -> bool:
  return True


class Invoice(models.Model):

    number = SequenceField(
      resolve_integrity_errors=_should_resolve_integrity_errors,
    )
```


#### Drawbacks

Since the technique implemented in `django-seq` is based on the concept of
synchronous/atomic transactions; concurrent Python processes mutating
the same sequence are not prevented to be started, but they will be waiting
for the current transaction to be committed or rolled back.

If a part of your system that generates IDs has heavy load, you may want
to follow a different approach that suitable for the use case. In some
situations implementing a queue to generate IDs using the low level API can
help to solve some tradeoff problems.


### Low Level API

`django_seq.models.AbstractSequence` provides two methods:

- `get_next_value`: Returns the next value of the sequence. Every time it's
    triggered, the sequence will be updated with the next value.
- `get_current_value`: Returns the current value of the sequence.
- `set_current_value`: Sets the current value of the sequence as the given
    value and returns the value back.


#### Using the low level API

Calling `get_next_value` or `set_current_value` always must be within a transaction.

```python
from django.db import transaction
from django_seq.models import get_sequence_model


Sequence = get_sequence_model()


with transaction.atomic():
    value = Sequence.get_next_value('projects.1.issues')
    assert Sequence.get_current_value('projects.1.issues') == value
```
