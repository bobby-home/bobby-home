#pragma once
#include <sstream>


struct Detection
{
	Detection(int c, const std::string &n, float conf, int x, int y, int w, int h)
		: category(c), name(n), confidence(conf), x(x), y(y), width(w), height(h)
	{
	}

	int category;
	std::string name;
	float confidence;

	int x;
	int y;
	int width;
	int height;

	std::string toString() const
	{
		std::stringstream output;
		output.precision(2);
		output << name << "[" << category << "] (" << confidence << ") @ " << x << "," << y << " " << width
			   << "x" << height;
		return output.str();
	}
};

