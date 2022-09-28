# INSTRUCTION

In here, 2 sample .mi file (using new input format) is already included, you can run this: 
Please don't forget to also add rule-builder/ to your path.

## Translation Process

```bash
../translate_g.py func_in.mi -l java -r ssd_safe-ssd_safe.o.vtable.mi --name FUNCIN
../translate_g.py func_cross.mi -l java -r ssd_safe-ssd_safe.o.vtable.mi --name FUNCROSS
```

## Building rule

```bash
rbuild FUNCIN.java DECLARE_RULE.java -j ssd_safe-1.0-SNAPSHOT.jar
rbuild FUNCROSS.java DECLARE_RULE.java -j ssd_safe-1.0-SNAPSHOT.jar
```

## Testing rule

```bash
rscan-py App.java FUNCIN
rscan-py App.java FUNCROWW
```



