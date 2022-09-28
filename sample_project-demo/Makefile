OBJS = io.o  rdc_lab_02.o rdc_lab_03.o rdc_lab_06.o rdc_lab_07.o rdc_lab_09.o main.o
TARGET = program
.PHONY: all clean

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) -o $@ $^

clean:
	rm -f $(TARGET) $(OBJS)
